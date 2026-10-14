#!/usr/bin/env python3
"""章节页结构检查：python3 tools/lint.py chapters/01.html …
查：小节标题和顺序、先下注和读后对照是否成对、论证骨架（SVG 和边读边填的表）、分节地图（每节一条、照抄原书小标题、词数、坐下分隔）、
词条（.en 重复、.loc 是否在原文那一段里、是否在自己那一节的小标题下、顺序、密度、trap 占比）、「先停下」的分界、
引用块（数量、不能引 {Q} 段落里别人的话）、另一边怎么说和对照今天（卡片数、结论标签、核对日期）、术语页链接、
图片、理解检查的题数、页面里的 <style>/<script>/写死的颜色、直引号、原书材料的路径。通用的几项在 ~/tutorials-deploy/scripts/lint_common.py。
00.html（开读之前）用另一张小节表，见 SECS0。"""
import os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.expanduser("~/tutorials-deploy/scripts"))
from lint_common import norm, check_entries, check_quotes, check_images, check_markup, counts

SECS = ["这一章在做什么", "读之前：先下注", "这一章的论证骨架", "分节地图", "背景：作者默认你知道的事",
        "这一章的经济学，先用中文过一遍", "词与短语", "读完：回到你的赌注", "另一边怎么说", "对照今天", "和本站其他书对照",
        "值得停下来的句子", "检查一下理解", "精彩回顾"]
SECS0 = ["这本书是怎么来的", "三个版本怎么配合", "全书的论证地图", "读之前：先下注", "分节地图", "背景：作者默认你知道的事",
         "词与短语", "读完：回到你的赌注", "作者十年后怎么看", "和本站其他书对照", "值得停下来的句子", "检查一下理解"]
OPTIONAL = {"和本站其他书对照"}
VERDICTS = {"成立", "部分成立", "被改写"}
GLOSS = os.path.join(ROOT, "glossary.html")
SISTERS = {"odyssey": "~/a_personal_odyssey", "letters": "~/a_man_of_letters", "cmc": "~/creating_modern_capitalism", "ggs": "~/gun_germs_and_steel",
           "hwgtn": "~/how_we_got_to_now", "feynman": "~/feynmans_rainbow", "summer": "~/the_door_into_summer", "aposd": "~/aposd"}
han = lambda s: len(re.findall(r"[一-鿿]", re.sub(r"<[^>]+>", "", s)))

def load(src):
    """读 source/text/NN.txt。返回 paras {段号: 文字}、quoted {是 {Q} 的段号}、secs [(节号, 小标题, 第一段, 最后一段, 词数)]。"""
    paras, quoted, secs = {}, set(), []
    for line in open(src, encoding="utf-8").read().splitlines():
        m = re.match(r"## §(\d+|附录[AB])(?: (.*))?$", line)
        if m: secs.append([m.group(1), m.group(2) or "", None, None, 0]); continue
        m = re.match(r"\[(\d+)\] (\{[QF]\} )?(.*)$", line)
        if m:
            p = int(m.group(1)); paras[p] = norm(m.group(3))
            if m.group(2) == "{Q} ": quoted.add(p)
            s = secs[-1]; s[2] = s[2] or p; s[3] = p
            if m.group(2) != "{F} ": s[4] += len(m.group(3).split())
    return paras, quoted, [tuple(s) for s in secs]

bad = 0
gloss_ids = set(re.findall(r'id="(g-[a-z0-9-]+)"', open(GLOSS, encoding="utf-8").read())) if os.path.exists(GLOSS) else set()
for path in sys.argv[1:]:
    t = open(path, encoding="utf-8").read(); errs = []
    nn = re.search(r"(\d\d)\.html$", path).group(1); N = int(nn)
    paras, quoted, secs = load(os.path.join(ROOT, f"source/text/{nn}.txt"))
    want_secs = SECS0 if N == 0 else SECS
    if f'<body data-chapter="{N}">' not in t: errs.append(f'<body> 应写成 <body data-chapter="{N}">')
    def part(a, *bs):
        if f"<h2>{a}</h2>" not in t: return ""
        i = t.find(f"<h2>{a}</h2>")
        ends = [t.find(f"<h2>{b}</h2>", i + 1) for b in bs] + [t.find("<h2>", i + 1)]
        ends = [e for e in ends if e > i]
        return t[i:min(ends)] if ends else t[i:]

    # 小节标题和顺序
    present = [s for s in want_secs if f"<h2>{s}</h2>" in t]
    for s in want_secs:
        if s not in present and s not in OPTIONAL: errs.append(f"缺少小节：{s}")
    pos = [t.find(f"<h2>{s}</h2>") for s in present]
    if pos != sorted(pos): errs.append("小节顺序不对，应为：" + " → ".join(want_secs))
    for s in re.findall(r"<h2>(.*?)</h2>", t):
        if s not in want_secs: errs.append(f"多出来的小节标题：{s}（标题一个字都不能改）")
    if N:
        g = re.search(r'<div class="gist">(.*?)</div>', t, flags=re.S)
        if not g: errs.append("「这一章在做什么」要有 <div class=\"gist\">")
        elif han(g.group(1)) > 200: errs.append(f"「这一章在做什么」{han(g.group(1))} 个汉字，超过 200")

    # 先下注 ↔ 读后对照
    pre = part("读之前：先下注")
    bets = re.findall(r'<div class="bet" data-key="([^"]+)">', pre)
    if not 1 <= len(bets) <= 2: errs.append(f"「读之前：先下注」要有 1–2 个 <div class=\"bet\" data-key>，现在 {len(bets)} 个")
    for k in bets:
        if not k.startswith(f"{nn}-"): errs.append(f"下注的 data-key 要以 {nn}- 开头：{k}")
        if f'<div class="payoff" data-bet="{k}"><div class="mine"></div>' not in part("读完：回到你的赌注"):
            errs.append(f"下注 {k} 在「读完：回到你的赌注」里没有对应的 <div class=\"payoff\" data-bet=\"{k}\"><div class=\"mine\"></div>…")
        if f'<textarea class="note" data-key="{k}-bet"' not in pre: errs.append(f"下注 {k} 要带一个 <textarea class=\"note\" data-key=\"{k}-bet\">")
    if N:
        if '<div class="crux">' not in pre: errs.append("「读之前」要有一个 <div class=\"crux\">")
        nq = len(re.findall(r"<li>", re.search(r'<ol class="qs">(.*?)</ol>', pre, flags=re.S).group(1))) if '<ol class="qs">' in pre else 0
        if not 2 <= nq <= 4: errs.append(f"「读之前」带着读的问题（<ol class=\"qs\">）应有 2–4 个，现在 {nq} 个")
    for k in re.findall(r'class="note" data-key="([^"]+)"', t):
        if not k.startswith(f"{nn}-"): errs.append(f"笔记的 data-key 要以 {nn}- 开头：{k}")

    # 论证骨架：SVG + 边读边填
    if N:
        sk = part("这一章的论证骨架")
        keys = re.findall(r'<input class="note" data-key="([^"]+)"', sk)
        if '<table class="findit">' not in sk or not 4 <= len(keys) <= 7: errs.append(f"「论证骨架」要有一张边读边填的表（<table class=\"findit\">），4–7 行，现在 {len(keys)} 行")
        if '<details class="reveal">' not in sk: errs.append("「论证骨架」的表后面要有 <details class=\"reveal\"> 对照")
        if "<svg" not in sk: errs.append("「论证骨架」要有一张自己画的 SVG")

    # 分节地图：每节一条，<b> 照抄小标题（开篇照抄第一段开头 4–7 个词）
    sm = part("分节地图")
    items = re.findall(r'<li data-sec="(\d+|附录[AB])"><b>(.*?)<span class="w">约 (\d+) 词</span></b><span class="what">(.*?)</span></li>', sm, flags=re.S)
    want = [s[0] for s in secs]
    if [k for k, *_ in items] != want: errs.append(f"分节地图的节号应为 {want}，实际是 {[k for k, *_ in items]}（写法照规范：<li data-sec><b>…<span class=\"w\">约 N 词</span></b><span class=\"what\">…</span></li>）")
    for (k, b, w, what), (sk_, title, p0, p1, words) in zip(items, secs):
        b = norm(re.sub(r"<[^>]+>", "", b)).strip("… ").strip()
        if title == "（开篇）":
            first = next(paras[p] for p in range(p0, p1 + 1) if p in paras and p not in quoted)
            if not (first.startswith(b) and 4 <= len(b.split()) <= 7): errs.append(f"分节地图 §{k}：开篇没有小标题，<b> 照抄第一段（不算引文）开头 4–7 个词：{b!r}")
        elif title and b != norm(title): errs.append(f"分节地图 §{k}：<b> 要一字不差地照抄小标题 {title!r}，现在是 {b!r}")
        elif not title and b != f"APPENDIX {k[-1]}": errs.append(f"分节地图 {k}：<b> 写 APPENDIX {k[-1]}")
        if abs(int(w) - words) > max(60, words * 0.1): errs.append(f"分节地图 §{k}：词数写的是 {w}，实际约 {words}")
        if han(what) > 50: errs.append(f"分节地图 §{k}：说明 {han(what)} 个汉字，超过 50")
    sits = len(re.findall(r'<li class="sit">', sm))
    total = sum(s[4] for s in secs)
    if total > 6000 and not 2 <= sits <= 4: errs.append(f"分节地图要用 <li class=\"sit\"> 分成 2–4 次坐下，现在 {sits} 次")

    # 词条：在自己那一节的小标题下
    words_sec = part("词与短语")
    rng = {s[0]: (s[2], s[3]) for s in secs}
    cur = None
    for m in re.finditer(r'<h3 class="sec-head" id="s(\d+|附录[AB])">|<div class="loc" data-p="(\d+)">', words_sec):
        if m.group(1): cur = m.group(1); continue
        p = int(m.group(2))
        if cur is None: errs.append(f"第 {p} 段的词条前面没有节的小标题 <h3 class=\"sec-head\" id=\"sK\">"); continue
        a, b = rng.get(cur, (0, -1))
        if not a <= p <= b: errs.append(f"第 {p} 段的词条放在了 §{cur} 下面（§{cur} 是第 {a}–{b} 段）")
    for k in re.findall(r'<h3 class="sec-head" id="s(\d+|附录[AB])">', words_sec):
        if k not in rng: errs.append(f"词与短语：没有 §{k} 这一节")
    errs += check_entries(t, paras, per_k=6, max_n=140, trap_ratio=1 / 3, scope="这一章")
    c0 = counts(t)
    if c0["词条"] and c0["trap"] > c0["词条"] * 0.7: errs.append(f"trap {c0['trap']}/{c0['词条']}，标得太宽（三分之一到七成为宜）")

    # 先停下的分界：在「词与短语」之后、「读完」之前，只有一处
    g = t.count('<div class="gate">')
    if g != 1: errs.append(f"要有且只有一处 <div class=\"gate\">（先停下，去读原书），现在 {g} 处")
    elif not (t.find("<h2>词与短语</h2>") < t.find('<div class="gate">') < t.find("<h2>读完：回到你的赌注</h2>")):
        errs.append("<div class=\"gate\"> 要放在「词与短语」之后、「读完：回到你的赌注」之前")

    # 引用块：不超过 3 处，只引作者自己的话
    errs += check_quotes(t, 3)
    for q in re.findall(r'<blockquote class="quote">(.*?)<cite>', t, flags=re.S):
        s = norm(re.sub(r"<[^>]+>", "", q)).strip("… ").strip()
        where = [p for p, v in paras.items() if s.replace("…", "") and all(x.strip() in v for x in s.split("…") if x.strip())]
        if not where: errs.append(f"引用块在原文里找不到（要一字不差，省略处用 …；引用别的章的话不行）：{s[:50]!r}")
        elif all(p in quoted for p in where): errs.append(f"引用块引的是 {{Q}} 段落（别人的话），只引作者自己写的：{s[:50]!r}")
        if len(s.replace("…", " ").split()) > 25: errs.append(f"引用块超过 25 个词：{s[:50]!r}")

    # 另一边怎么说
    if N:
        ct = part("另一边怎么说")
        nc = len(re.findall(r'<div class="counter" data-title="[^"]+">', ct))
        if not 2 <= nc <= 4: errs.append(f"「另一边怎么说」应有 2–4 张 <div class=\"counter\" data-title=\"…\">，现在 {nc} 张")
    # 对照今天（00 页叫「作者十年后怎么看」，卡片格式一样）
    td = part("对照今天" if N else "作者十年后怎么看")
    cards = re.findall(r'<div class="today" data-verdict="([^"]*)">(.*?)</dl>', td, flags=re.S)
    for h4 in re.findall(r'<div class="today"[^>]*><h4>(.*?)</h4>', td, flags=re.S):
        if not h4.startswith("书里的说法："): errs.append(f"「对照今天」卡片标题要写成被检验的说法：<h4>书里的说法：……</h4>，现在是 {h4[:20]!r}")
    if '<ul class="verdicts">' not in td: errs.append("「对照今天」开头要有结论图例 <ul class=\"verdicts\">（照抄样板）")
    if not 2 <= len(cards) <= 4: errs.append(f"「对照今天」应有 2–4 张卡片（<div class=\"today\" data-verdict>），现在 {len(cards)} 张")
    for v, body in cards:
        if v not in VERDICTS: errs.append(f"「对照今天」的结论只能是 {'、'.join(sorted(VERDICTS))}：{v!r}")
        dts = re.findall(r"<dt>(.*?)</dt>", body)
        if dts[:1] != ["书里"] or len(dts) != 3 or dts[2] != "今天": errs.append("「对照今天」每张卡片三行：<dt>书里</dt>、<dt>当时（…）</dt>、<dt>今天</dt>")
        if not re.search(r'<span class="asof">核对于 20\d\d-\d\d', body): errs.append("「对照今天」每张卡片要写 <span class=\"asof\">核对于 YYYY-MM…</span>")

    # 精彩回顾：一句话 + 5–8 张卡片，每张标节号、不超过 100 个汉字
    if N:
        rc = part("精彩回顾")
        if '<p class="recall-line">' not in rc: errs.append("「精彩回顾」要有 <p class=\"recall-line\"><b>一句话：</b>…</p>")
        items_r = re.findall(r'<div class="item"><b>(.*?)</b><p>(.*?)</p><span class="sec">(§[^<]+)</span></div>', rc, flags=re.S)
        if not 5 <= len(items_r) <= 8 or len(items_r) != rc.count('<div class="item">'): errs.append(f"「精彩回顾」应有 5–8 张卡片，写法 <div class=\"item\"><b>标题</b><p>…</p><span class=\"sec\">§k</span></div>，现在认出 {len(items_r)} 张")
        for b_, p_, _ in items_r:
            if han(p_) > 100: errs.append(f"「精彩回顾」{b_}：{han(p_)} 个汉字，超过 100")
    else: items_r = []

    # 链接：术语页、本站其他书
    for gid in re.findall(r'href="\.\./glossary\.html#(g-[^"]+)"', t):
        if gid not in gloss_ids: errs.append(f"术语页里没有 #{gid}")
    for site, u in re.findall(r'href="/([a-z]+)/(chapters/[^"#]+)', t):
        d = SISTERS.get(site)
        if not d or not os.path.exists(os.path.join(os.path.expanduser(d), u)): errs.append(f"本站其他书的链接不对：/{site}/{u}")

    # 译本也受版权保护：页面正文里不能有和译本连续 12 个汉字以上相同的片段
    zp = os.path.join(ROOT, f"source/text/zh/{nn}.txt")
    if os.path.exists(zp):
        zt = re.sub(r"[^一-鿿]", "", open(zp, encoding="utf-8").read())
        body = re.sub(r"<[^>]+>", " ", re.sub(r"<(svg|script|style)\b.*?</\1>", " ", t, flags=re.S))
        hits = set()
        for run in re.findall(r"[一-鿿]{12,}", body):
            for i in range(len(run) - 11):
                if run[i:i + 12] in zt: hits.add(run[i:i + 12]); break
        for x in sorted(hits): errs.append(f"和译本有 12 个汉字以上相同的片段：{x}（页面上不能出现译本的句子）")

    errs += check_images(t, path, min_photos=4, min_svgs=2)
    c = counts(t)
    if not 6 <= c["检查题"] <= 8: errs.append(f"理解检查应有 6–8 题，现在 {c['检查题']} 题")
    errs += check_markup(t, r"\.epub|\.pdf|c\d\d\.xml|part0\d+|filepos|source/")
    print(("✗" if errs else "✓"), path, " ".join(f"{k} {v}" for k, v in c.items()), f"地图 {len(items)} 坐下 {sits} 对照今天 {len(cards)} 回顾 {len(items_r)} 原文 {total} 词")
    for e in errs: print("    " + e)
    bad += bool(errs)
sys.exit(1 if bad else 0)
