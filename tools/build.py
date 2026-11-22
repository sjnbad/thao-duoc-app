import re, json, math, unicodedata, sys
RAW = "/home/claude/raw/"
BOOKS = [
 ("The Lost Book of Herbal Remedies.txt", "The Lost Book of Herbal Remedies", "Nicole Apelian & Claude Davis", True),
 ("Valerie_Ann_Worwood_The_Complete_Book_of_Essential_Oils_and_Aromatherapy.txt", "The Complete Book of Essential Oils and Aromatherapy", "Valerie Ann Worwood", False),
 ("Ancient_Remedies_for_Modern_Life_The_Secrets_to_Healing,_Resilience.txt", "Ancient Remedies", "Dr. Josh Axe", False),
 ("Curing With Cayenne.txt", "Curing With Cayenne", "Sam Biser & Dr. Richard Schulze", False),
 ("Survival_Herbal_Remedies.txt", "Survival Herbal Remedies", "", False),
 ("The_Lost_Book_of_Remedies.txt", "The Lost Book of Remedies", "Claude Davis", False),
 ("The Autoimmune Protocol.txt", "The Autoimmune Protocol", "Frank Newman", False),
 ("The_Lost_Book_Disease_Prevention.txt", "The Lost Book of a Disease-Free Life", "", False),
 ("The_Lost_Book_of_a_Healthy_Life.txt", "The Lost Book of a Healthy Life", "", False),
 ("The_Lost_Book_of_Youth.txt", "The Lost Book of Youth", "", False),
 ("The_Lost_Book_Superfoods.txt", "The Lost Book of Superfoods", "", False),
 ("The_Lost_Garden_of_Eden.txt", "The Lost Garden of Eden", "", False),
]
lex = json.load(open("/home/claude/build/lexicon.json"))
herbs = json.load(open("/home/claude/build/herbs.json")); herbs.pop("steam", None)

def kw_re(k):
    k = k.lower()
    return re.compile(r"\b" + re.escape(k) + (r"\w*" if " " not in k and len(k) > 3 else r"\b"))

all_kws = sorted({k.lower() for s in lex for k in s["en"]})
kw_res = {k: kw_re(k) for k in all_kws}
HEADER_JUNK = re.compile(r"^(The Lost Book.*|Curing With Cayenne by.*|© SURVIVAL HERBAL.*|The Autoimmune Protocol\s*\d*|\d+|\d+ of \d+|Page \d+ of \d+|The Complete Book of Essential Oils and Aromatherapy)$")

passages = []
dups = set()
HEAD_CAPS = re.compile(r"^[A-Z0-9][A-Z0-9 ,’'&/()\-–:]{3,70}$")
HEAD_AXE = re.compile(r"^([A-Z][A-Z ’'\-()/&,]{3,60})\. (.*)$")
NOISE = re.compile(r"(BLEND|DROPS|CARE KIT|TABLE|CONTENTS|CHAPTER|PART [A-Z]+|^NOTE|^WARNING|^CAUTION|ISBN|^[IVX]+$)")
plant_names = []
herb_txt = open(RAW + BOOKS[0][0], encoding="utf-8").read()
for m in re.finditer(r"\n\n([A-Z][A-Za-z’'\- ]{2,40}),\n([A-Z][a-z]+ [a-z\-]+)", herb_txt):
    nm = m.group(1).strip()
    if not re.search(r"Photo|Close|by ", nm): plant_names.append(nm)
plant_names = sorted(set(plant_names), key=len, reverse=True)
warns = {}
for bi, (fn, title, author, _p) in enumerate(BOOKS):
    txt = open(RAW + fn, encoding="utf-8", errors="ignore").read()
    long_sec = bi in (1, 2)
    pages = txt.split("\f")
    h = ""
    buf = []; bufp = 1
    out = []
    def flush():
        global buf
        if buf:
            t = re.sub(r"\s{2,}", " ", " ".join(buf)).strip()
            out.append((bufp, t, h))
        buf = []
    for pi, pg in enumerate(pages, start=1):
        lines = [l.strip() for l in pg.split("\n")]
        for l in lines:
            if HEADER_JUNK.match(l): continue
            if not l:
                cur = sum(len(x) for x in buf)
                target = 1500 if (long_sec and h) else 520
                if cur >= target: flush()
                continue
            ma = HEAD_AXE.match(l) if bi == 2 else None
            isCaps = HEAD_CAPS.match(l) and sum(c.isalpha() for c in l) >= 4 and not NOISE.search(l)
            if ma or isCaps:
                flush()
                h = (ma.group(1) if ma else l).strip(" :").title()
                bufp = pi
                if ma: buf = [l]
                continue
            if not buf: bufp = pi
            if buf and buf[-1].endswith("-") and l[:1].islower():
                buf[-1] = buf[-1][:-1] + l
            else:
                buf.append(l)
            if sum(len(x) for x in buf) > 2600: flush()
        # page boundary: continue section across pages
    flush()
    for pi, t, hh in out:
        t = re.sub(r"\.{4,}\s*\d*", " … ", t)
        if bi == 0 and t.startswith("Warning"):
            for nm in plant_names:
                if nm.lower() in t.lower():
                    w = re.split(r"(?:[A-Z][A-Za-z’'\- ]{2,40}, [A-Z][a-z]+ [a-z]+|Recipes|Medicinal Use|Edible Use|Harvesting|Identification)", t)[0]
                    warns.setdefault(nm, w[:600].strip()); break
        if len(t) < 60: continue
        key = re.sub(r"\W", "", t.lower())[:200]
        if key in dups: continue
        dups.add(key)
        lo = t.lower()
        if lo.count("…") > 3: continue
        if not any(r.search(lo) for r in kw_res.values()): continue
        if re.match(r"(Contents|Glossary of Therapeutic)", t): continue
        if sum(c.isdigit() for c in t) / max(len(t), 1) > 0.06: continue  # index pages
        if len(hh) < 6 or hh in ("Introduction", "Appendix", "Zdravetz", "Illness", "Applications"): hh = ""
        passages.append({"b": bi, "p": pi, "t": t, "pl": hh})

# Vietnamese sinus article (manual transcription, short summary in VN)
print("passages", len(passages), "chars", sum(len(p["t"]) for p in passages), file=sys.stderr)

# keyword IDF
N = len(passages)
df = {k: 0 for k in all_kws}
for p in passages:
    lo = p["t"].lower()
    for k, r in kw_res.items():
        if r.search(lo): df[k] += 1
kwi = {k: round(math.log((N + 1) / (df[k] + 1)) * (1.4 if " " in k else 1.0), 2) for k in all_kws}


import subprocess
vn = json.loads(subprocess.check_output(["node","-e","process.stdout.write(JSON.stringify(require('/home/claude/build/guide.js').VNARTICLE))"]))
BOOKS.append(("", "Tự chữa bệnh viêm xoang không cần thuốc (Chua Viem Xoang.pdf)", "Dương Anh Hùng – Báo Nông nghiệp VN", False))
passages.append({"b": len(BOOKS)-1, "p": 1, "t": vn, "pl": "Viêm xoang", "tags": ["sinus","stuffy","runny"]})
TR = json.load(open("/home/claude/build/tr.json"))
VI = {}
for i, p in enumerate(passages):
    v = TR.get(p["t"][:160])
    if v: VI[i] = v
print("translated", len(VI), file=sys.stderr)
out = {
  "books": [{"t": b[1], "a": b[2]} for b in BOOKS], "plants": plant_names,
  "lex": lex, "kwi": kwi, "herbs": herbs, "warn": warns,
  "VI": VI, "P": [[p["b"], p["p"], p["t"], p["pl"] or ""] + ([p["tags"]] if p.get("tags") else []) for p in passages],
}
json.dump(out, open("/home/claude/build/data.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(sorted(df.items(), key=lambda x: -x[1])[:25], file=sys.stderr)
print("warns", len(warns), file=sys.stderr)
