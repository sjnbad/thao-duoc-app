"""Tạo site/lib.json từ các bản tóm tắt tiếng Việt /home/claude/sum/<slug>/NN.md"""
import glob, json, re, os
import markdown

BOOKS = [  # slug, tên sách, tên file PDF gốc
    ("herbal", "The Lost Book of Herbal Remedies", "The Lost Book of Herbal Remedies"),
    ("axe", "Ancient Remedies (Josh Axe)", "Ancient_Remedies_for_Modern_Life_The_Secrets_to_Healing,_Resilience"),
    ("worwood", "The Complete Book of Essential Oils (Worwood)", "Valerie_Ann_Worwood_The_Complete_Book_of_Essential_Oils_and_Aromatherapy"),
    ("cayenne", "Curing With Cayenne", "Curing With Cayenne"),
    ("survival", "Survival Herbal Remedies", "Survival_Herbal_Remedies"),
    ("aip", "The Autoimmune Protocol", "The Autoimmune Protocol"),
    ("lb_prev", "The Lost Book: Disease Prevention", "The_Lost_Book_Disease_Prevention"),
    ("lb_healthy", "The Lost Book of a Healthy Life", "The_Lost_Book_of_a_Healthy_Life"),
    ("lb_remedies", "The Lost Book of Remedies", "The_Lost_Book_of_Remedies"),
    ("lb_youth", "The Lost Book of Youth", "The_Lost_Book_of_Youth"),
    ("lb_superfoods", "The Lost Book: Superfoods", "The_Lost_Book_Superfoods"),
    ("eden", "The Lost Garden of Eden", "The_Lost_Garden_of_Eden"),
    ("tisserand", "Essential Oil Safety (Tisserand & Young)", "Robert_Tisserand_and_Rodney_Young_Auth_Essential_Oil_Safety_A_Guide"),
    ("viemxoang", "Tự chữa bệnh viêm xoang không cần thuốc", "Chua Viem Xoang"),
]

def md2html(s):
    s = s.strip()
    if not s:
        return ""
    h = markdown.markdown(s, extensions=["extra"])
    if h.startswith("<p>") and h.endswith("</p>") and h.count("<p>") == 1:
        h = h[3:-4]
    return h

books, E = [], []
for slug, title, fname in BOOKS:
    parts = sorted(glob.glob(f"/home/claude/sum/{slug}/*.md"))
    if not parts:
        continue
    bi = len(books)
    books.append({"t": title, "f": fname + "_Viet.pdf"})
    section = ""
    cur = None
    for p in parts:
        for ln in open(p, encoding="utf-8").read().split("\n"):
            if ln.startswith("# "):
                section = ln[2:].strip()
                cur = None
                continue
            m = re.match(r"## (.+?)(?:\s+—\s+tr\.\s*([\d–\-, ]+))?\s*$", ln)
            if m:
                pg = m.group(2) or ""
                first = re.match(r"\d+", pg)
                cur = {"b": bi, "s": section, "t": m.group(1).strip(), "p": int(first.group()) if first else 0,
                       "pg": pg.strip(), "intro": [], "li": []}
                E.append(cur)
                continue
            if cur is None:
                if ln.strip() and E and E[-1]["b"] == bi:  # phần tiếp của mục trước (đầu file mới)
                    cur = E[-1]
                else:
                    continue
            if re.match(r"\s+(\d+\.|-) ", ln) and cur["li"]:
                cur["li"][-1] += "<br>" + ln.strip()
            elif re.match(r"\s*- ", ln):
                cur["li"].append(re.sub(r"^\s*- ", "", ln))
            elif ln.strip():
                if cur["li"]:  # dòng nối tiếp của gạch đầu dòng trước
                    cur["li"][-1] += " " + ln.strip()
                else:
                    cur["intro"].append(ln.strip())

out = []
for e in E:
    out.append([e["b"], e["s"], e["t"], e["p"], e["pg"], md2html(" ".join(e["intro"])),
                [md2html(x) for x in e["li"]]])
json.dump({"books": books, "E": out}, open("/home/claude/build/site/lib.json", "w", encoding="utf-8"),
          ensure_ascii=False, separators=(",", ":"))
print(len(books), "books", len(out), "entries", os.path.getsize("/home/claude/build/site/lib.json"))
