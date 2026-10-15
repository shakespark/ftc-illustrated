// Free to Choose 导读：共享脚本。注入顶栏、章头（三个版本的位置）、读法切换、章末导航、页脚；
// 接管分节地图（打勾、纸书页码、录音位置、译本小节名）、词条的「记下」和筛选、先下注和读后对照、本地笔记、首页目录和全书回顾。
// 骨架来自 Creating Modern Capitalism 伴读的 cm.js，下注来自枪炮伴读。
// localStorage 键一律带 fc- 前缀（全站各教程同一个域名）：fc-done-N、fc-sec-N-节号、fc-star-NN-词条、fc-note-…、fc-bet-…、fc-mode-N、fc-theme。
(() => {
  const CH = window.FC_CHAPTERS || [], READY = new Set(window.FC_READY || []);
  const SECS = window.FC_SECS || {}, ZH = window.FC_ZH || {};
  const ROOT = document.currentScript.src.replace(/assets\/fc\.js.*$/, "");
  const LS = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { v == null || v === "" ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch {} },
    keys(prefix) { try { return Object.keys(localStorage).filter((k) => k.startsWith(prefix)); } catch { return []; } },
  };
  const h = (tag, attrs = {}, ...kids) => {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) k === "class" ? (el.className = v) : k.startsWith("on") ? (el[k] = v) : el.setAttribute(k, v);
    el.append(...kids.filter((x) => x != null));
    return el;
  };
  const pad = (n) => String(n).padStart(2, "0");
  const chHref = (n) => `${ROOT}chapters/${pad(n)}.html`;
  const chLabel = (n) => (n === 0 ? "开读之前" : `第 ${n} 章`);
  const chTitle = (c) => (c.n === 0 ? "开读之前 · 序言与引言" : `${chLabel(c.n)} · ${c.t}`);
  const isDone = (n) => LS.get(`fc-done-${n}`) === "1";
  const secDone = (n, k) => LS.get(`fc-sec-${n}-${k}`) === "1";
  const meta = (n) => SECS[n] || { words: 0, min: 0, secs: [] };
  const pages = (n) => { const s = meta(n).secs; return s.length ? `${s[0].p.split("–")[0]}–${s[s.length - 1].p.split("–").pop()}` : ""; };
  const nSecs = (n) => meta(n).secs.length;
  // 英文的第 k 节 → 译本的小节名。译本的开篇没有标题；第 4 章原书 §6 WHAT IS POLITICALLY FEASIBLE? 译本没有单列，并在「我们应当做什么」里。
  function zhSec(n, k) {
    const z = (ZH[n] || {}).secs || [];
    if (String(k).startsWith("附录")) return z.find((s) => s.startsWith(String(k))) || null;
    k = Number(k);
    if (n === 0) return z[k] || null;                       // 译本多一篇「推荐序」，排在最前
    if (k === 1) return "";                                 // 开篇
    if (n === 4 && k === 6) return null;
    return z[k - 2 - (n === 4 && k > 6 ? 1 : 0)] || null;
  }
  const badges = (c) => [
    h("span", { class: "badge" }, c.topic),
    h("span", { class: "badge" }, `约 ${meta(c.n).words} 词 · ${nSecs(c.n)} 节 · 录音约 ${meta(c.n).min} 分钟`),
  ];

  const saved = LS.get("fc-theme");
  if (saved) document.documentElement.dataset.theme = saved;
  function themeBtn() {
    return h("button", { class: "btn", "aria-label": "切换深色/浅色", onclick() {
      const dark = document.documentElement.dataset.theme ? document.documentElement.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
      const next = dark ? "light" : "dark";
      document.documentElement.dataset.theme = next; LS.set("fc-theme", next);
    } }, "深/浅");
  }
  const curN = () => (document.body.dataset.chapter == null ? null : Number(document.body.dataset.chapter));

  function mountChrome() {
    const n = curN(), c = CH.find((x) => x.n === n);
    document.body.prepend(h("div", { class: "topbar" }, h("div", { class: "topbar-inner" },
      h("a", { class: "home", href: `${ROOT}index.html` }, "Free to Choose · 导读"),
      h("span", { class: "crumb" }, c ? chTitle(c) : ""),
      themeBtn())));
    document.body.append(h("footer", { class: "site-footer" },
      h("a", { href: "https://beian.miit.gov.cn/", target: "_blank", rel: "noopener" }, "京ICP备18057656号-1")));
    if (!c) return;
    const main = document.querySelector("main");
    document.title = `${chTitle(c)} · Free to Choose 导读`;
    const z = ZH[n] || {};
    main.prepend(h("div", { class: "chapter-head" },
      h("div", { class: "kicker" }, n === 0 ? c.en : `Chapter ${n} · ${c.en}`),
      h("h1", {}, n === 0 ? "开读之前" : `${chLabel(n)}　${c.t}`),
      h("dl", { class: "where" },
        h("dt", {}, "纸书"), h("dd", {}, `Harvest 版（1990）第 ${pages(n)} 页`),
        h("dt", {}, "Kindle"), h("dd", {}, n === 0 ? "Foreword to the Harvest Edition、Preface、Introduction" : `Chapter ${n}`),
        h("dt", {}, "Audible"), h("dd", {}, `约 ${meta(n).min} 分钟（James Adams 朗读）`),
        h("dt", {}, "译本"), h("dd", {}, n === 0 ? "珍藏版序言、初版序言、引言" : `张琦译本 ${z.t || c.t}`)),
      h("div", { class: "badges" }, ...badges(c))));
    if (n > 0) mountMode(n, main.querySelector(".chapter-head"));
    const prev = CH.find((x) => x.n === n - 1), next = CH.find((x) => x.n === n + 1);
    const done = h("button", { class: "btn" });
    const paint = () => { done.textContent = isDone(n) ? `✓ 已读完${n ? "这一章" : ""}` : `标记：${n ? "这一章" : "这一篇"}读完了`; done.setAttribute("aria-pressed", isDone(n)); };
    done.onclick = () => { LS.set(`fc-done-${n}`, isDone(n) ? null : "1"); paint(); };
    paint();
    main.append(h("div", { class: "chapter-end" }, done, h("div", { class: "nav" },
      prev && READY.has(prev.n) ? h("a", { class: "btn", href: chHref(prev.n) }, `← ${chLabel(prev.n)}`) : null,
      h("a", { class: "btn", href: `${ROOT}index.html` }, "目录"),
      next && READY.has(next.n) ? h("a", { class: "btn primary", href: chHref(next.n) }, `${chLabel(next.n)} →`) : null)));
  }

  // 读法切换：这一章读英文还是读译本。读译本时词条收起，分节地图把译本的小节名放在前面。键 fc-mode-N（"zh" 或不存）。
  function mountMode(n, head) {
    const key = `fc-mode-${n}`;
    const set = (zh) => { document.body.classList.toggle("mode-zh", zh); b1.setAttribute("aria-pressed", String(!zh)); b2.setAttribute("aria-pressed", String(zh)); };
    const b1 = h("button", { class: "btn", onclick() { LS.set(key, null); set(false); } }, "英文原版");
    const b2 = h("button", { class: "btn", onclick() { LS.set(key, "zh"); set(true); } }, "张琦译本");
    const c = (window.FC_CHAPTERS || []).find((x) => x.n === n);
    head.after(h("div", { class: "mode" }, h("span", {}, "这一章我读："), b1, b2,
      c && c.zr ? h("p", { class: "zrel" }, h("b", {}, `译本：${c.zr[0]}。`), c.zr[1]) : null));
    set(LS.get(key) === "zh");
  }

  // 「词与短语」那一节包进 <section class="words">，读译本时收起，留一行可以展开
  function wrapWords() {
    const hd = [...document.querySelectorAll("main > h2")].find((x) => x.textContent.trim() === "词与短语");
    if (!hd) return;
    const sec = h("section", { class: "words" });
    hd.before(sec);
    let el = hd;
    while (el && !(el !== hd && el.tagName === "H2") && !(el.classList && el.classList.contains("gate"))) { const nx = el.nextElementSibling; sec.append(el); el = nx; }
    const k = sec.querySelectorAll(".entry").length;
    sec.before(h("div", { class: "words-folded" }, h("b", {}, "词与短语"), `　这一章你读译本，${k} 条英文词条已收起。`,
      h("button", { class: "btn", onclick() { document.body.classList.add("show-words"); } }, "展开")));
  }

  // 词条：<div class="entry [trap]"><div class="en">…</div><div class="loc" data-p="段号">原句里的 4–7 个词</div><div class="zh">…</div><div class="note">…</div></div>
  function wireEntries() {
    const entries = [...document.querySelectorAll(".entry")];
    if (!entries.length) return;
    const n = pad(curN());
    const first = entries[0];
    const count = h("span", { class: "count" });
    const mk = (label, cls) => h("button", { class: "btn", "aria-pressed": String(!cls), onclick(e) {
      document.body.classList.remove("only-traps", "only-starred");
      if (cls) document.body.classList.add(cls);
      bar.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b === e.currentTarget)));
    } }, label);
    const bar = h("div", { class: "toolbar" }, mk("全部", ""), mk("只看「每个字都认识」", "only-traps"), mk("只看我记下的", "only-starred"), count);
    (first.previousElementSibling?.matches("h3.sec-head") ? first.previousElementSibling : first).before(bar, h("p", { class: "empty-note" }, "还没有记下任何词条。回到「全部」，点词条右边的「记下」。"));
    const refresh = () => {
      const k = entries.filter((e) => e.classList.contains("starred")).length;
      document.body.classList.toggle("none-starred", k === 0);
      count.textContent = `共 ${entries.length} 条 · 已记下 ${k}`;
    };
    for (const e of entries) {
      const en = e.querySelector(".en"), text = en.textContent.trim();
      const key = `fc-star-${n}-${text}`;
      if (e.classList.contains("trap")) en.append(h("span", { class: "tag" }, "每个字都认识"));
      const btn = h("button", { class: "btn star" });
      const paint = () => { btn.textContent = e.classList.contains("starred") ? "已记下" : "记下"; };
      if (LS.get(key)) e.classList.add("starred");
      btn.onclick = () => {
        const on = e.classList.toggle("starred");
        LS.set(key, on ? JSON.stringify({ zh: e.querySelector(".zh")?.textContent.trim() || "" }) : null);
        paint(); refresh();
      };
      paint(); en.after(btn);
    }
    refresh();
  }

  // 分节地图：<ol class="secmap"><li class="sit">第一次坐下 …</li><li data-sec="2"><b>原书小标题</b><span class="w">约 600 词</span><span class="what">…</span></li>…</ol>
  // 每节加：读过了的勾、§k、纸书页码、录音里大约第几分钟、译本里的小节名；有词条的节加「词条 ↓」。
  function wireSecmap() {
    const n = curN();
    for (const li of document.querySelectorAll(".secmap li[data-sec]")) {
      const k = li.dataset.sec, key = `fc-sec-${n}-${k}`;
      const s = meta(n).secs.find((x) => x.k === k);
      const box = h("input", { type: "checkbox", "aria-label": `第 ${k} 节读过了` });
      box.checked = secDone(n, k); li.classList.toggle("done", box.checked);
      box.onchange = () => { LS.set(key, box.checked ? "1" : null); li.classList.toggle("done", box.checked); };
      li.prepend(box, h("span", { class: "k" }, String(k).startsWith("附录") ? k : `§${k}`));
      const z = zhSec(n, k);
      const where = h("span", { class: "at" },
        s ? h("span", {}, `纸书 p.${s.p}`) : null,
        s ? h("span", {}, s.min ? `录音约第 ${s.min} 分钟起` : "录音从头开始") : null,
        h("span", { class: "zt" }, n === 4 && k === "6" ? "译本「我们应当做什么」后半，从正文里「■什么是政治上可行的」那一行起"
          : z ? `译本「${z}」` : z === "" ? "译本：章名之后、第一个小标题之前" : "译本：没有单列小标题"));
      li.querySelector("b")?.after(where);
      if (document.getElementById(`s${k}`)) li.append(h("a", { class: "jump", href: `#s${k}` }, "词条 ↓"));
    }
  }
  const secProgress = (c) => {
    const k = meta(c.n).secs.filter((s) => secDone(c.n, s.k)).length;
    return k && !isDone(c.n) ? h("span", { class: "sp" }, `　已读 ${k} 节`) : null;
  };

  // 本地笔记：<input class="note" data-key="01-f1"> / <textarea class="note" data-key="01-oneline">，键 fc-note-01-f1
  function wireNotes() {
    for (const el of document.querySelectorAll("input.note, textarea.note")) {
      const key = `fc-note-${el.dataset.key}`;
      el.value = LS.get(key) || "";
      let tip = null;
      if (el.tagName === "TEXTAREA") { tip = h("div", { class: "note-tip" }, el.value ? "已保存在本机浏览器" : "写下来会自动保存在本机浏览器"); el.after(tip); }
      let t = null;
      el.addEventListener("input", () => { clearTimeout(t); t = setTimeout(() => { LS.set(key, el.value.trim() ? el.value : null); if (tip) tip.textContent = "已保存在本机浏览器"; }, 400); });
    }
  }

  // 先下注：<div class="bet" data-key="01-a"><div class="q">…</div><div class="opts"><button>…</button>…</div><textarea class="note" data-key="01-a-bet"></textarea></div>
  // 读后对照：<div class="payoff" data-bet="01-a"><div class="mine"></div><p>…</p></div>，显示读者当初押了什么、写了什么。键 fc-bet-01-a（选项序号）
  function wireBets() {
    for (const bet of document.querySelectorAll(".bet")) {
      const key = `fc-bet-${bet.dataset.key}`;
      const btns = [...bet.querySelectorAll(".opts button")];
      const paint = () => { const v = LS.get(key); btns.forEach((b, k) => b.classList.toggle("sel", String(k) === v)); };
      btns.forEach((b, k) => (b.onclick = () => { LS.set(key, LS.get(key) === String(k) ? null : String(k)); paint(); fillPayoffs(); }));
      paint();
    }
    fillPayoffs();
  }
  function fillPayoffs() {
    for (const po of document.querySelectorAll(".payoff")) {
      const k = po.dataset.bet, mine = po.querySelector(".mine");
      if (!mine) continue;
      const bet = document.querySelector(`.bet[data-key="${k}"]`);
      const v = LS.get(`fc-bet-${k}`);
      const choice = bet && v != null ? bet.querySelectorAll(".opts button")[Number(v)] : null;
      const note = LS.get(`fc-note-${k}-bet`) || "";
      const q = bet?.querySelector(".q")?.textContent.trim();
      mine.textContent = [q ? `当初的问题：${q}` : "", choice ? `你押的是：${choice.textContent.trim()}` : "", note ? `你写的理由：${note}` : ""].filter(Boolean).join("\n");
      if (!choice && !note) mine.dataset.empty = "1"; else delete mine.dataset.empty;
    }
  }

  // 首页：目录、进度、我的词本
  function mountHome() {
    const toc = document.getElementById("toc");
    if (!toc) return;
    for (const c of CH) {
      const ready = READY.has(c.n);
      toc.append(h("li", {}, h("a", Object.assign({ class: (isDone(c.n) ? "done " : "") + (ready ? "" : "todo") }, ready ? { href: chHref(c.n) } : {}),
        h("span", { class: "n" }, isDone(c.n) ? "✓" : c.n === 0 ? "序" : String(c.n)),
        h("span", { class: "t" }, c.n === 0 ? "开读之前" : c.t, h("span", { class: "te" }, c.en)),
        h("span", { class: "b" }, ...(ready ? badges(c) : [h("span", { class: "badge" }, c.topic), h("span", { class: "badge" }, "待写")])),
        c.d ? h("span", { class: "d" }, c.d, secProgress(c)) : null)));
    }
    const doneN = CH.filter((c) => isDone(c.n)).length;
    const p = document.getElementById("progress");
    if (p) p.append(h("div", { class: "progress" }, Object.assign(h("i"), { style: `width:${(100 * doneN) / CH.length}%` })), h("p", { class: "lede" }, `已读完 ${doneN} / ${CH.length}`));
    const wb = document.getElementById("wordbook");
    if (wb) {
      const keys = LS.keys("fc-star-").sort();
      if (!keys.length) wb.append(h("p", { class: "lede" }, "还是空的。在章节页里点词条右边的「记下」，它们会汇总到这里。"));
      for (const k of keys) {
        const m = k.match(/^fc-star-(\d\d)-(.*)$/); if (!m) continue;
        let zh = ""; try { zh = JSON.parse(LS.get(k)).zh; } catch {}
        wb.append(h("div", {}, h("b", {}, m[2]), h("span", {}, zh), h("a", { href: chHref(Number(m[1])) }, chLabel(Number(m[1])))));
      }
    }
  }

  // 全书回顾（recap.html 的 #recap）：读各个已完成章节页的「精彩回顾」汇总。章节页改了，这里自动跟着变。
  async function mountRecap() {
    const box = document.getElementById("recap");
    if (!box) return;
    let shown = 0;
    for (const c of CH) {
      if (!READY.has(c.n)) continue;
      let doc;
      try { doc = new DOMParser().parseFromString(await (await fetch(chHref(c.n))).text(), "text/html"); } catch { continue; }
      const line = doc.querySelector(".recall-line"), items = doc.querySelector(".recall");
      if (!items) continue;
      for (const a of items.querySelectorAll(".sec")) a.replaceWith(h("a", { class: "sec", href: chHref(c.n) }, a.textContent));
      box.append(h("section", { class: "recap-ch" },
        h("h2", {}, h("a", { href: chHref(c.n) }, chTitle(c))),
        h("p", { class: "lede" }, c.en),
        line ? document.importNode(line, true) : null, document.importNode(items, true)));
      shown++;
    }
    if (!shown) box.append(h("p", { class: "lede" }, "还没有写好的章节。"));
  }

  document.addEventListener("DOMContentLoaded", () => { mountChrome(); wireSecmap(); wrapWords(); wireEntries(); wireNotes(); wireBets(); mountHome(); mountRecap(); });
  // 跨设备同步：模块在首页仓库里（/_home/sync.js），所有教程站共用。只在线上加载；本地预览要联调时设 localStorage["sync-dev"] = "1"
  // 上线前要把 fc- 加进 sync.js 的 PREFIXES 和 sync_server.py 的 KEY_RE，见 ~/tutorials-deploy/README.md。
  try { if (location.hostname === "t.miaowuao.cn" || localStorage.getItem("sync-dev")) document.head.append(Object.assign(document.createElement("script"), { src: "/_home/sync.js" })); } catch (e) {}
  window.FC = { h, LS, ROOT, chHref, chLabel, isDone, zhSec };
})();
