# Free to Choose · 导读

陪读 *Free to Choose*（Milton and Rose Friedman，1980；Harvest 版 1990）的静态站，一章一页。读者手上有英文纸书、Kindle、Audible 和张琦译本（机械工业出版社），
一章一章交替着读，所以每页同时照顾英文和译本：章头写三个版本的位置，每章有「这一章我读：英文原版 / 张琦译本」的开关。
线上地址 https://t.miaowuao.cn/ftc/ ，仓库 shakespark/ftc-illustrated。推送到 main 就由 GitHub Actions 部署。

## 目录

| 路径 | 作用 |
|---|---|
| `index.html` | 首页：这本书、三个版本怎么配合、目录、我的词本 |
| `chapters/NN.html` | `00` 开读之前（序言和引言），`01`–`10` 是原书各章。样板是 `01.html` |
| `glossary.html` | 全书术语（英文、译本译法、解释），章节页链过来，主编维护 |
| `recap.html` | 全书回顾：`fc.js` 读各个已完成章节页的「精彩回顾」汇总 |
| `assets/chapters.js` | 目录数据（原书章名、译本章名、主题、一句话）和已完成的章 |
| `assets/sections.js` | 各节的原书小标题、词数、Harvest 版页码、录音分钟数、译本小节名。由 `tools/extract.py` 和 `tools/extract_zh.py` 生成，不要手改 |
| `assets/fc.js`、`assets/style.css` | 共享脚本和样式。骨架来自 Creating Modern Capitalism 伴读，下注和反方卡片来自枪炮伴读，读法切换是本站加的 |
| `AUTHORING.md` | 章节页编写规范（公共部分见 `~/tutorials-deploy/AUTHORING-COMMON.md`） |
| `tools/` | `extract.py`、`extract_zh.py` 提取文本；`lint.py` 本站的结构检查（含「和译本有 12 个汉字以上相同」的检查）；`overlap.py`、`check.mjs`、`fetch_img.py` 转调 `~/tutorials-deploy/scripts/` 里的共用版 |
| `source/` | 原书和译本的 epub、提取的文本、截图、任务说明、Python 虚拟环境，以及 `zh-cuts-china.md`（译本里涉及中国的删改和错译，原文译文对照，本地参考）。**不入库、不部署** |

localStorage 键都带 `fc-` 前缀：`fc-done-N`（N 是 0–10）、`fc-sec-N-节号`、`fc-star-NN-词条`、`fc-note-…`、`fc-bet-…`、`fc-mode-N`、`fc-theme`。

## 重新提取文本

```sh
python3 -I tools/extract.py      # 读 source/epub/OPS/，写 source/text/00.txt … 10.txt、notes.txt 和 assets/sections.js 的 FC_SECS
python3 -I tools/extract_zh.py   # 读 source/epub-zh/text/，写 source/text/zh/00.txt … 10.txt 和 assets/sections.js 的 FC_ZH（要在 extract.py 之后跑）
```

录音分钟数按每分钟 160 词估（Audible 版 12 小时 15 分，全书约 11.8 万词），改 `extract.py` 里的 `WPM`。
