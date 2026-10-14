#!/usr/bin/env python3
"""从张琦译本（机械工业出版社，珍藏版）的 epub 解压目录 source/epub-zh/ 提取文本到 source/text/zh/NN.txt。
只给作者对照位置用（读者读译本时，页面要能指到译本里的同一处），页面里不能出现译文。
  `## ■标题` 是译本的小节标题（对应英文的 §k），`### 标题` 是更小一级；每行一段，行首 [段号]；{Q} 是缩进的引文。
  00.txt：推荐序（译本独有）、珍藏版序言、初版序言、引言。10.txt 末尾带两个附录。
同时把译本的章名、小节名写进 assets/sections.js 的 FC_ZH（只有标题）。"""
import html, json, os, re
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
EP = os.path.join(ROOT, "source/epub-zh/text")
OUT = os.path.join(ROOT, "source/text/zh")
PARTS = {0: range(3, 7), 1: range(8, 16), 2: range(17, 24), 3: range(25, 33), 4: range(34, 43), 5: range(44, 52), 6: range(53, 68),
         7: range(69, 77), 8: range(78, 85), 9: range(86, 96), 10: list(range(97, 113)) + [114, 115]}

def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()

os.makedirs(OUT, exist_ok=True)
zh = {}
for n, parts in PARTS.items():
    lines, k, title, secs = [], 0, "", []
    for i in parts:
        t = open(os.path.join(EP, f"part{i:04d}.html"), encoding="utf-8").read()
        t = t[t.find("<body"):]
        t = re.sub(r'<sup\b.*?</sup>|<a class="pcalibre1 pcalibre"[^>]*>\s*\[\d+\]\s*</a>', "", t, flags=re.S)
        for tag, attrs, body in re.findall(r"<(h\d|p)\b([^>]*)>(.*?)</\1>", t, flags=re.S):
            s = clean(body)
            if not s: continue
            if tag == "h1" or (tag == "h2" and not s.startswith("■")):
                if n == 0 or s.startswith("附录"): lines.append(f"## ■{s}"); secs.append(s)
                else: title = s
                continue
            if tag == "h2": lines.append(f"## {s}"); secs.append(s[1:]); continue
            if tag == "h3": lines.append(f"### {s}"); continue
            k += 1; lines.append(f"[{k}] {'{Q} ' if 'ziti4' in attrs else ''}{s}")
    open(os.path.join(OUT, f"{n:02d}.txt"), "w", encoding="utf-8").write(f"# {title or '序言与引言'}\n\n" + "\n".join(lines) + "\n")
    zh[n] = {"t": title, "secs": secs}
    print(f"{n:02d} {title:16s} {k:4d} 段  " + " | ".join(secs))

p = os.path.join(ROOT, "assets/sections.js")
s = open(p, encoding="utf-8").read().split("\n// 张琦译本")[0].rstrip("\n")
s += ("\n// 张琦译本（机械工业出版社）的章名和小节名，由 tools/extract_zh.py 生成，不要手改。t 章名；secs 按顺序是各个 ■ 小节"
      "（不含开篇，开篇在译本里没有标题）。\n" "window.FC_ZH = " + json.dumps(zh, ensure_ascii=False) + ";\n")
open(p, "w", encoding="utf-8").write(s)
