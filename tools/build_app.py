"""Dựng app/index.html từ bản tóm tắt tiếng Việt (summaries/), từ điển triệu chứng và
phần tóm tắt nhanh (tools/app_data/). Không dùng văn bản gốc của sách.

Dữ liệu được nén và mã hoá rồi nhúng vào app, để nội dung không nằm ở dạng chữ thường
trong mã nguồn trang.

Dùng:  python3 tools/build_app.py
"""
import base64, glob, json, os, re, zlib
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUM = os.path.join(ROOT, "summaries")
DATA = os.path.join(ROOT, "tools", "app_data")
KEY = b"thao-duoc/books-of-healing/2026"

BOOKS = [  # slug, tên sách
    ("herbal", "The Lost Book of Herbal Remedies"),
    ("axe", "Ancient Remedies (Josh Axe)"),
    ("worwood", "The Complete Book of Essential Oils (Worwood)"),
    ("cayenne", "Curing With Cayenne"),
    ("survival", "Survival Herbal Remedies"),
    ("aip", "The Autoimmune Protocol"),
    ("lb_prev", "The Lost Book: Disease Prevention"),
    ("lb_healthy", "The Lost Book of a Healthy Life"),
    ("lb_remedies", "The Lost Book of Remedies"),
    ("lb_youth", "The Lost Book of Youth"),
    ("lb_superfoods", "The Lost Book: Superfoods"),
    ("eden", "The Lost Garden of Eden"),
    ("tisserand", "Essential Oil Safety (Tisserand & Young)"),
    ("viemxoang", "Tự chữa bệnh viêm xoang không cần thuốc"),
]
WILD_BOOKS = {"herbal", "survival"}      # sách về cây hoang dã Bắc Mỹ
NO_OPTION_BOOKS = {"tisserand"}         # sách bảng an toàn, không phải bài thuốc
# các phần không phải bài thuốc chữa bệnh (món ăn, làm đẹp, vật nuôi, cây độc…): vẫn có trong Thư viện
NO_OPTION_SECTIONS = re.compile(r"Công thức nấu ăn|vật nuôi|Spa tại nhà|Làm đẹp|ngôi nhà|Khu vườn|Nấu ăn với tinh dầu|"
                                r"Hồ sơ các loại tinh dầu|Dầu nền và hydrolat|Thông tin an toàn|gây chết người|Làm vườn|"
                                r"Herbal Remedies — Tóm tắt", re.I)


def md2html(s):
    s = s.strip()
    if not s:
        return ""
    h = markdown.markdown(s, extensions=["extra"])
    if h.startswith("<p>") and h.endswith("</p>") and h.count("<p>") == 1:
        h = h[3:-4]
    return h


def read_lib():
    books, E = [], []
    for slug, title in BOOKS:
        parts = sorted(glob.glob(os.path.join(SUM, slug, "*.md")))
        if not parts:
            continue
        bi = len(books)
        books.append({"t": title, "s": slug})
        section, cur = "", None
        for p in parts:
            for ln in open(p, encoding="utf-8").read().split("\n"):
                if ln.startswith("# "):
                    section, cur = ln[2:].strip(), None
                    continue
                m = re.match(r"## (.+?)(?:\s+—\s+tr\.\s*([\d–\-, ]+))?\s*$", ln)
                if m:
                    pg = m.group(2) or ""
                    first = re.match(r"\d+", pg)
                    cur = {"b": bi, "s": section, "t": m.group(1).strip(),
                           "p": int(first.group()) if first else 0, "pg": pg.strip(), "intro": [], "li": []}
                    E.append(cur)
                    continue
                if cur is None:
                    if ln.strip() and E and E[-1]["b"] == bi:
                        cur = E[-1]
                    else:
                        continue
                if re.match(r"\s+(\d+\.|-) ", ln) and cur["li"]:
                    cur["li"][-1] += "<br>" + ln.strip()
                elif re.match(r"\s*- ", ln):
                    cur["li"].append(re.sub(r"^\s*- ", "", ln))
                elif ln.strip():
                    if cur["li"]:
                        cur["li"][-1] += " " + ln.strip()
                    else:
                        cur["intro"].append(ln.strip())
    return books, E


# ---------- độ khó ----------
# 1 = dễ kiếm / làm nhanh, 2 = cần mua thêm / cần pha chế, 3 = khó kiếm / cầu kỳ
COMMON = ["gừng", "tỏi", "nghệ", "sả", "mật ong", "chanh", "hành", "tiêu đen", "hạt tiêu", "bạc hà", "húng",
          "rau mùi", "mùi tây", "tía tô", "ngải cứu", "nha đam", "lô hội", "dứa", "đu đủ", "chuối", "giấm",
          "muối", "trà xanh", "dầu dừa", "ô liu", "thì là", "cà rốt", "yến mạch", "sữa chua", "ớt", "cayenne",
          "củ cải", "bắp cải", "dưa chuột", "rau má", "diếp cá", "rau sam", "mã đề", "ổi", "hạt chia",
          "hạt lanh", "vừng", "táo", "dừa", "cam", "bưởi", "khoai", "bí", "cải xoong", "bầu", "mướp",
          "đậu", "quế", "đinh hương", "nước hầm xương", "trứng", "cần tây", "rau dền", "củ dền",
          "dưa hấu", "lựu", "nho", "chè", "atiso", "nấm hương", "kiều mạch (buckwheat"]
BUY = ["cúc la mã", "hoa cúc", "oải hương", "hương thảo", "tía tô đất", "nữ lang", "cúc tím", "echinacea",
       "cam thảo", "linh chi", "nấm", "nhũ hương", "mộc dược", "tràm trà", "khuynh diệp", "bạch đàn",
       "hoa bia", "cỏ xạ hương", "xô thơm", "kinh giới", "hương nhu", "tulsi", "nhân sâm", "sâm",
       "ashwagandha", "bồ công anh", "tầm ma", "cơm cháy", "elderberry", "thục quỳ", "du trơn", "ích mẫu",
       "cỏ ban", "kế sữa", "mullein", "cúc thơm", "hoa anh thảo", "dâm bụt", "hoa hồi", "bạch quả",
       "rau mùi tây", "thì là tây", "hạt cây gai", "nguyệt quế", "hoa hồng", "lô hội", "hoa nhài",
       "phỉ", "witch hazel", "goldenseal", "thanh hao", "hải ly", "tảo"]
TOXIC = re.compile(r"chết người|rất độc|cực độc|độc tính cao|tử vong|gây sẩy thai|rất thận trọng|chỉ người có kinh nghiệm", re.I)
P3 = re.compile(r"cồn thuốc|\bcồn\b|vodka|rượu mạnh|ngâm[^.;]{0,60}(tuần|tháng)|\d\s*(–\s*\d+\s*)?tuần|thuốc mỡ|sáp ong|ép lạnh|"
                r"ép dầu|chưng cất|sắc kép|lên men|đóng nang|glycerin|dầu ngâm|ngâm dầu|sấy|"
                r"(đun|liu riu|sắc)[^.;]{0,50}\d+\s*(–\s*\d+\s*)?giờ", re.I)
P2 = re.compile(r"tinh dầu|\bgiọt\b|\bđun\b|\bsắc\b|siro|đắp|xông|\bmg\b|viên nang|ngâm|nấu|khuếch tán|dầu nền|giã", re.I)


EASY = re.compile(r"(?<!\w)(ăn|nhai|ngậm|uống)\s[^.;]{0,25}(thìa|tép|lát|cốc|ly|nước ấm|nước nóng)", re.I)


def plain(s):
    return re.sub(r"<[^>]+>", " ", s)


OILS = re.compile(r"tinh dầu|\bgiọt\b|dầu nền", re.I)


def prep_level(txt):
    t = plain(txt)
    if P3.search(t):
        return 3
    if OILS.search(t):                     # cần mua tinh dầu; trộn từ 4 thứ trở lên thì tính là khó
        return 3 if t.count("+") >= 3 else 2
    if EASY.search(t):
        return 1
    if t.count("+") >= 3:
        return 3
    if P2.search(t):
        return 2
    return 1


FIRST_BUY = ["cam thảo", "táo gai", "tía tô đất", "hạt dẻ ngựa"]


def has(term, text):
    return re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text) is not None


def access_level(e, slug):
    name = e["t"].split("(")[0].lower()
    full = e["t"].lower()
    if any(has(c, name) for c in FIRST_BUY):
        return 2
    if any(has(c, name) for c in COMMON):
        return 1
    if any(has(c, full) for c in BUY):
        return 2
    return 3 if slug in WILD_BOOKS else 0       # 0 = không phải mục cây thuốc, xét theo nội dung


def main():
    books, E = read_lib()
    out = []
    for e in E:
        slug = books[e["b"]]["s"]
        lis = [md2html(x) for x in e["li"]]
        herb = bool(re.search(r"\([^)]*[A-Za-z]{3}", e["t"])) and slug not in NO_OPTION_BOOKS
        meta = {
            "a": access_level(e, slug) if herb else 0,
            "r": [prep_level(x) for x in lis],
            "x": 1 if any(TOXIC.search(plain(x)) for x in lis) else 0,
            "h": 1 if herb else 0,
            "o": 0 if slug in NO_OPTION_BOOKS or NO_OPTION_SECTIONS.search(e["s"]) else 1,
        }
        out.append([e["b"], e["s"], e["t"], e["p"], e["pg"], md2html(" ".join(e["intro"])), lis, meta])

    guide = json.load(open(os.path.join(DATA, "guide.json"), encoding="utf-8"))
    lex = json.load(open(os.path.join(DATA, "lexicon.json"), encoding="utf-8"))
    payload = {"lib": {"books": [{"t": b["t"]} for b in books], "E": out},
               "guide": guide["guide"], "gbooks": guide["books"], "redflag": guide["redflag"],
               "lex": lex["lex"], "herbs": lex["herbs"]}
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    z = c.compress(raw) + c.flush()
    z = bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(z))
    blob = base64.b64encode(z).decode()

    tpl = open(os.path.join(ROOT, "app", "app.tpl.html"), encoding="utf-8").read()
    html = tpl.replace("/*BLOB*/", blob, 1).replace("/*KEY*/", KEY.decode(), 1)
    open(os.path.join(ROOT, "app", "index.html"), "w", encoding="utf-8").write(html)
    print(len(books), "sách,", len(out), "mục; dữ liệu", len(raw), "→", len(blob), "byte; index.html", len(html))


if __name__ == "__main__":
    main()
