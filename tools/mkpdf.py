"""Ghép các file tóm tắt <slug>/NN.md thành một PDF tiếng Việt.
Dùng: python3 mkpdf.py <slug> "<Tên sách gốc>" "<tên file pdf ra>"
"""
import sys, glob, os, subprocess, html, re
import markdown

slug, title, outname = sys.argv[1], sys.argv[2], sys.argv[3]
parts = sorted(glob.glob(f"/home/claude/sum/{slug}/*.md"))
md = "\n\n".join(open(p, encoding="utf-8").read() for p in parts)

# ---- chèn hình minh họa từ sách gốc theo số trang của mỗi mục ----
import json
IMG = f"/home/claude/sum/img/{slug}"
imgs = json.load(open(f"{IMG}/index.json")) if os.path.exists(f"{IMG}/index.json") else []
cover_img = next((m for m in imgs if m["p"] <= 2), None)
H = re.compile(r"^## .+?—\s+tr\.\s*([\d–\-, ]+)\s*$")
def pages_of(sp):
    out = set()
    for part in sp.split(","):
        nums = [int(x) for x in re.findall(r"\d+", part)]
        if len(nums) == 1: out.add(nums[0])
        elif len(nums) >= 2 and nums[1] >= nums[0] and nums[1] - nums[0] < 60:
            out.update(range(nums[0], nums[1] + 1))
    return out
lines = md.split("\n")
heads = []   # (line index, pages)
for i, ln in enumerate(lines):
    m = H.match(ln)
    if m: heads.append((i, pages_of(m.group(1))))
assign = {}
used = set()
for im in imgs:
    if im is cover_img: continue
    best = None
    hits = [(min(pg), hi) for hi, (li, pg) in enumerate(heads) if im["p"] in pg]
    if hits: best = max(hits)[1]
    if best is None:   # gần nhất phía trước, cách tối đa 2 trang
        cand = [(im["p"] - max(pg), hi) for hi, (li, pg) in enumerate(heads) if pg and 0 < im["p"] - max(pg) <= 2]
        if cand: best = min(cand)[1]
    if best is not None and len(assign.get(best, [])) < 4:
        assign.setdefault(best, []).append(im)
SLUG_PLANT = slug in ("herbal", "survival", "eden", "aip")
LATIN = re.compile(r"\b[A-Z][a-z]*\.? (?:[a-z]+\.? )?[a-z]{4,}\b")
def caption(hi):
    t = re.sub(r"\s+—\s+tr\..*$", "", lines[heads[hi][0]][3:]).strip()
    t = re.sub(r"[*_]", "", t)
    m = re.match(r"(.+?)\s*\((.+)\)\s*$", t)
    METHOD = re.compile(r"infusion|decoction|salve|extract|poultice|tincture|syrup|oil|bath|compress|tea\b|wash|liniment|capsule|powder|cream|steam|chapter|recipe", re.I)
    if m and METHOD.search(m.group(1) + " " + m.group(2)) and "Mormon" not in t:
        return f"Minh họa: {t}"
    if m and (LATIN.search(m.group(2)) or (not METHOD.search(m.group(2)) and not METHOD.search(m.group(1)) and SLUG_PLANT and re.fullmatch(r"[A-Za-z' .,/&-]+", m.group(2)))):
        first = re.split(r"[,;]", m.group(2))[0].strip()
        name = m.group(1).strip()
        if first and not LATIN.fullmatch(first) and first.lower() != name.lower():
            name += f" ({first})"
        if re.match(r"(Muối|Mật ong|Giấm|Đất sét|Than|Bột)\b", name) or not LATIN.search(m.group(2)) and re.match(r"(Dầu|Thuốc|Cách|Siro|Cồn|Trà|Nước|Làm|Ngâm|Chiết|Bài|Công thức|Chương|Phần)\b", name): return f"Minh họa: {t}"
        if re.match(r"(Nấm|Địa y|Tảo|Rong)", name): return f"Đây là {name[0].lower()+name[1:]}"
        return f"Đây là cây {name}"
    return f"Minh họa: {t}"
CAPS = json.load(open(f"{IMG}/captions.json")) if os.path.exists(f"{IMG}/captions.json") else {}
def fig(im, hi):
    cls = "fig wide" if im["w"] > im["h"] * 1.3 else "fig"
    return (f'<figure class="{cls}"><img src="file://{IMG}/{im["f"]}">'
            f'<figcaption>{html.escape(CAPS.get(im["f"][:-4]) or caption(hi))}</figcaption></figure>')
ends = [h[0] for h in heads[1:]] + [len(lines)]
for hi in sorted(assign, reverse=True):
    # chèn ngay sau tiêu đề và đoạn giới thiệu in nghiêng (nếu có)
    end = heads[hi][0] + 1
    while end < len(lines) and not lines[end].strip(): end += 1
    if end < len(lines) and lines[end].startswith("*") and not lines[end].startswith("* "):
        while end < len(lines) and lines[end].strip() and not re.match(r"\s*([-*]|\d+\.) ", lines[end]): end += 1
    else:
        end = heads[hi][0] + 1
    block = '<div class="figs">' + "".join(fig(im, hi) for im in assign[hi]) + "</div>"
    lines[end:end] = ["", block, ""]
md = "\n".join(lines)
NIMG = sum(len(v) for v in assign.values())
# python-markdown cần một dòng trống trước danh sách
_out, _prev = [], ""
for _ln in md.split("\n"):
    _ln = re.sub(r"^  (\d+\.|-) ", r"    \1 ", _ln)
    if re.match(r"[-*] ", _ln) and not re.match(r"\s*([-*]|\d+\.) ", _prev) and _prev.strip():
        _out.append("")
    _out.append(_ln)
    _prev = _ln
md = "\n".join(_out)
body = markdown.markdown(md, extensions=["extra", "sane_lists"])

# mục lục từ các tiêu đề # và ##
toc = []
def anchor(m):
    level, text = m.group(1), m.group(2)
    i = len(toc)
    toc.append((level, re.sub("<[^>]+>", "", text)))
    return f'<h{level} id="s{i}">{text}</h{level}>'
body = re.sub(r"<h([12])>(.*?)</h\1>", anchor, body)
toc_html = "".join(
    f'<li class="t{lv}"><a href="#s{i}">{html.escape(t)}</a></li>' for i, (lv, t) in enumerate(toc))

doc = f"""<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8">
<title>{html.escape(title)} — Tóm tắt tiếng Việt</title>
<style>
@page {{ size: A4; margin: 18mm 16mm 18mm 16mm; }}
body {{ font-family: "Noto Serif", "DejaVu Serif", Georgia, serif; font-size: 11pt; line-height: 1.45; color:#1d1d1d; }}
h1 {{ font-family: "Noto Sans","DejaVu Sans",sans-serif; color:#2f5d3a; font-size:17pt; border-bottom:2px solid #2f5d3a; padding-bottom:3pt; margin-top:22pt; page-break-before: always; }}
h2 {{ font-family: "Noto Sans","DejaVu Sans",sans-serif; color:#24452c; font-size:13pt; margin:16pt 0 4pt; page-break-after: avoid; }}
h3 {{ font-size:12pt; }}
p, li {{ orphans:2; widows:2; }}
ul {{ margin:3pt 0 6pt 0; padding-left:16pt; }}
li {{ margin:2pt 0; }}
em {{ color:#444; }}
.cover {{ text-align:center; padding-top:70mm; page-break-after: always; }}
.cover h1 {{ border:none; page-break-before:auto; font-size:24pt; }}
.cover p {{ font-size:12pt; color:#444; }}
.note {{ border:1px solid #c9a227; background:#fff8e1; padding:8pt 10pt; font-size:10pt; margin-top:30mm; text-align:left; }}
.toc {{ page-break-after: always; }}
.toc h1 {{ page-break-before:auto; }}
.toc ul {{ list-style:none; padding-left:0; columns:2; column-gap:14pt; font-size:9.5pt; }}
.toc li.t1 {{ font-weight:bold; margin-top:6pt; }}
.toc li.t2 {{ padding-left:8pt; }}
.toc a {{ color:#1d1d1d; text-decoration:none; }}
.figs {{ display:flex; flex-wrap:wrap; gap:8pt; margin:4pt 0 10pt; page-break-inside:avoid; }}
.fig {{ margin:0; text-align:center; page-break-inside:avoid; }}
.fig img {{ max-height:55mm; max-width:82mm; border:1px solid #ddd; border-radius:3pt; }}
.fig.wide img {{ max-width:170mm; max-height:95mm; }}
.fig figcaption {{ font-size:8.5pt; color:#2f5d3a; font-style:italic; max-width:82mm; margin:2pt auto 0; font-family:"Noto Sans","DejaVu Sans",sans-serif; }}
.coverimg {{ max-height:85mm; max-width:120mm; margin-bottom:8mm; box-shadow:0 1pt 4pt #999; }}
.cover {{ padding-top:30mm !important; }}
</style></head><body>
<div class="cover">
{('<img class="coverimg" src="file://'+IMG+'/'+cover_img["f"]+'">') if cover_img else ''}
<h1>{html.escape(title)}</h1>
<p>Bản tóm tắt tiếng Việt</p>
<p>Viết lại bằng lời tóm tắt, không phải bản dịch nguyên văn. Số trang "tr." là trang PDF của sách gốc.</p>
<div class="note"><b>Lưu ý an toàn:</b> Đây là tài liệu tham khảo về thảo dược theo sách, không thay cho khám chữa bệnh.
Bệnh nặng, sốt cao kéo dài, khó thở, đau ngực, chảy máu nhiều, ngộ độc, trẻ nhỏ, người mang thai/cho con bú,
người đang dùng thuốc — hãy hỏi bác sĩ/dược sĩ. Cấp cứu: gọi 115. Các dòng "<i>Gợi ý thực hành (không có trong sách)</i>"
và "[Ghi chú của app]" là phần bổ sung, không phải nội dung sách.</div>
</div>
<div class="toc"><h1>Mục lục</h1><ul>{toc_html}</ul></div>
{body}
</body></html>"""

os.makedirs("/home/claude/sum/out", exist_ok=True)
hp = f"/home/claude/sum/out/{slug}.html"
open(hp, "w", encoding="utf-8").write(doc)
pdf = f"/home/claude/sum/out/{outname}"
subprocess.run(["/usr/bin/google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu",
                "--no-pdf-header-footer", f"--print-to-pdf={pdf}", "file://" + hp],
               check=True, capture_output=True)
print(pdf, os.path.getsize(pdf), "images:", NIMG)
