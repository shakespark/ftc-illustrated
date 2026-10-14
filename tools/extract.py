#!/usr/bin/env python3
"""从本机的 epub 解压目录（source/epub/OPS/）提取文本到 source/text/NN.txt。
  00.txt  开读之前：§1 Foreword to the Harvest Edition（1990）、§2 Preface（1979）、§3 Introduction
  01–10   十章。§1 （开篇）是第一个小标题之前的部分；§k 是原书印出来的小标题（全大写，照抄）；
          `### 小标题` 是更小一级的标题（原书斜体单独一行，不算一节）
  10.txt  末尾另有 §附录A、§附录B（原书的两个附录，第 10 章讨论的东西）
每行一段，行首 [段号]（每个文件内连续编号）。段落标记：{Q} 缩进的引文（多为别人的话、报刊、法律条文）；
{F} 原书这里有一张图表（图不提取）。尾注号已去掉；*词* 是原书的斜体。
每个 `## §` 下面一行 `%p 起–止` 是这一节在 Harvest 版（1990）纸书里的页码。
另存 source/text/notes.txt（原书尾注，核对事实用）。"""
import html, json, os, re
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
EP = os.path.join(ROOT, "source/epub/OPS")
OUT = os.path.join(ROOT, "source/text")

def read(name):
    t = open(os.path.join(EP, name), encoding="utf-8").read()
    t = t[t.find("<body"):]
    t = re.sub(r"<br\s*/?>", " ", t)                                        # 换行当空格
    t = re.sub(r'<a class="footnoteref"[^>]*>.*?</a>', "", t, flags=re.S)   # 尾注号
    t = re.sub(r"<(em|i)\b[^>]*>(.*?)</\1>", r"*\2*", t, flags=re.S)
    t = re.sub(r'<a id="p([0-9ivxl]+)"\s*/>', r"⟦\1⟧", t)                   # 纸书页码锚点
    t = re.sub(r'<img [^>]*class="art"[^>]*/>', "⟦FIG⟧", t)
    return t

def clean(s):
    s = html.unescape(re.sub(r"<[^>]+>", "", s))
    s = re.sub(r"\s+", " ", s).strip()
    return s.replace("* *", " ").replace("**", "")

def tokens(t):
    """按出现顺序给出 (种类, 文字, 是否在 blockquote 里)。种类：h1 h2 p sub（单独一行的斜体小标题）。"""
    pos, inq = 0, False
    for m in re.finditer(r"<blockquote>|</blockquote>|<(h\d|p|li)\b([^>]*)>(.*?)</\1>", t, flags=re.S):
        if m.group(0) == "<blockquote>": inq = True; continue
        if m.group(0) == "</blockquote>": inq = False; continue
        tag, attrs, body = m.group(1), m.group(2), m.group(3)
        yield tag, attrs, body, inq

class Doc:
    def __init__(self):
        self.lines, self.k, self.page, self.secs, self.sec_page = [], 0, None, [], None
    def pages_in(self, body):
        for p in re.findall(r"⟦([0-9ivxl]+)⟧", body): self.page = p
    def section(self, title):
        self.close()
        self.secs.append([title, 0]); self.lines.append(f"## §{len(self.secs)} {title}" if not title.startswith("附录") else f"## §{title}")
        self.lines.append("%p ?"); self.sec_start = self.page; self.sec_idx = len(self.lines) - 1
    def close(self):
        if self.secs: self.lines[self.sec_idx] = f"%p {self.sec_start}–{self.page}"
    def para(self, txt, mark=""):
        if not self.secs: self.section("（开篇）")
        self.k += 1; self.lines.append(f"[{self.k}] {mark}{txt}"); self.secs[-1][1] += len(txt.split())

def run(files, out, title, sections_from_h1=False):
    d = Doc()
    for f in files:
        t = read(f)
        for tag, attrs, body, inq in tokens(t):
            d.pages_in(body)
            if d.secs and d.sec_start is None: d.sec_start = d.page
            raw = clean(re.sub(r"⟦[0-9ivxl]+⟧", "", body))
            if "⟦FIG⟧" in body:
                d.para("原书这里有一张图表（不提取）", "{F} "); continue
            if tag == "h1" or (tag == "h2" and "chaptersubtitle" in attrs) or (tag == "h1" and "fronttitle" in attrs):
                if sections_from_h1 and tag == "h1": d.section({"FOREWORD TO THE HARVEST EDITION": "Foreword to the Harvest Edition"}.get(raw, raw.title() if raw.isupper() else raw))
                continue
            if tag == "h2" and "backsectiontitle" in attrs:
                d.section("附录" + raw.split()[-1]); continue
            if tag == "h2" and "sectiontitle" in attrs:
                d.section(raw); continue
            if tag == "h2": continue
            if not raw or 'class="right"' in attrs or 'class="center"' in attrs: continue
            if re.fullmatch(r"\*[^*]{1,80}\*", raw) and not inq and 'class="left"' in attrs:
                d.lines.append(f"### {raw.strip('*')}"); continue
            d.para(raw, "{Q} " if inq else "")
    d.close()
    body = "\n".join(d.lines)
    open(os.path.join(OUT, out), "w", encoding="utf-8").write(f"# {title}\n\n{body}\n")
    print(f"{out}  {len(d.secs):2d} 节 {d.k:4d} 段 {sum(w for _, w in d.secs):6d} 词   " + " | ".join(f"{s[:22]} {w}" for s, w in d.secs))
    return d

os.makedirs(OUT, exist_ok=True)
TITLES = ["The Power of the Market", "The Tyranny of Controls", "The Anatomy of Crisis", "Cradle to Grave", "Created Equal",
          "What's Wrong with Our Schools?", "Who Protects the Consumer?", "Who Protects the Worker?", "The Cure for Inflation", "The Tide Is Turning"]
run(["front05.xml", "front06.xml", "front08.xml"], "00.txt", "0 Foreword · Preface · Introduction", sections_from_h1=True)
for n in range(1, 11):
    run([f"c{n:02d}.xml"] + (["back01.xml"] if n == 10 else []), f"{n:02d}.txt", f"{n} {TITLES[n - 1]}")

# 尾注
t = read("back02.xml")
with open(os.path.join(OUT, "notes.txt"), "w", encoding="utf-8") as f:
    for tag, attrs, body, inq in tokens(t):
        s = clean(re.sub(r"⟦[0-9ivxl]+⟧", "", body))
        if s: f.write(("## " if tag.startswith("h") else "") + s + "\n")

# 各节的元数据（只有原书的小标题、词数、页码，没有正文）→ assets/sections.js，章节页的分节地图和章头用
WPM = 160   # Audible 版（James Adams 朗读，12 小时 15 分）全书约 11.8 万词，折合每分钟约 160 词
meta = {}
for n in range(0, 11):
    secs, cur = [], None
    for line in open(os.path.join(OUT, f"{n:02d}.txt"), encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("## §"):
            m = re.match(r"## §(\S+?)(?: (.*))?$", line)
            k, t = (m.group(1), m.group(2) or "") if not line.startswith("## §附录") else (line[4:], "")
            cur = {"k": k, "t": t, "w": 0, "p": ""}; secs.append(cur)
        elif line.startswith("%p ") and cur: cur["p"] = line[3:]
        elif line.startswith("[") and cur: cur["w"] += len(line.split()) - 1
    at = 0
    for s in secs: s["min"] = round(at / WPM); at += s["w"]
    meta[n] = {"words": at, "min": round(at / WPM), "secs": secs}
with open(os.path.join(ROOT, "assets/sections.js"), "w", encoding="utf-8") as f:
    f.write("// 由 tools/extract.py 生成，不要手改。每章各节：k 节号，t 原书小标题（开篇为「（开篇）」），w 词数，p Harvest 版纸书页码，\n"
            f"// min 这一节在本章录音里大约第几分钟开始（按每分钟 {WPM} 词估）。words / min：全章词数和录音分钟数。\n")
    f.write("window.FC_SECS = " + json.dumps(meta, ensure_ascii=False, indent=None).replace('}, {', '},\n  {').replace('], "', '],\n "') + ";\n")
