// 全书目录。n: 章号（0 是「开读之前」：Foreword、Preface、Introduction）；en: 原书标题；t: 张琦译本的章名（一字不差）；
// tv: 1980 年同名电视片里对应的一集；topic: 这一章管的那块公共政策；d: 一句话（本站写的）。
// 词数、节、页码、录音分钟数在 sections.js（tools/extract.py 生成）。
window.FC_CHAPTERS = [
  { n: 0, en: "Foreword · Preface · Introduction", t: "序言与引言", topic: "全书的框架", d: "两个「奇迹」和一条主线：经济自由与政治自由" },
  { n: 1, en: "The Power of the Market", t: "市场的力量", topic: "价格与政府的边界", d: "一支铅笔、价格的三种功能、政府该做的四件事" },
  { n: 2, en: "The Tyranny of Controls", t: "管制的专横", topic: "贸易与计划", d: "关税护着少数人，计划拖垮印度，管制伤及言论" },
  { n: 3, en: "The Anatomy of Crisis", t: "危机的解析", topic: "大萧条与联储", d: "大萧条是联储失职造成的货币崩溃，不是市场失灵" },
  { n: 4, en: "Cradle to Grave", t: "从摇篮到坟墓", topic: "福利国家", d: "好心为什么办坏事：花别人的钱，替别人办事" },
  { n: 5, en: "Created Equal", t: "生而平等", topic: "平等", d: "三种平等：机会平等护自由，结果平等要强制" },
  { n: 6, en: "What's Wrong with Our Schools?", t: "我们的学校出了什么问题", topic: "教育", d: "公立学校的毛病、代金券，和穷人补贴的大学" },
  { n: 7, en: "Who Protects the Consumer?", t: "谁在保护消费者", topic: "监管机构", d: "管制机构为什么常替被管的行业办事" },
  { n: 8, en: "Who Protects the Worker?", t: "谁在保护工人", topic: "工会与劳动", d: "谁在保护工人：作者说不是工会和政府，是别的雇主" },
  { n: 9, en: "The Cure for Inflation", t: "通货膨胀的对策", topic: "货币与通胀", d: "通胀只来自印钱，治它要先吃一段苦" },
  { n: 10, en: "The Tide Is Turning", t: "潮流在转变", topic: "政治与宪法", d: "特殊利益为何总赢，作者开出修宪的药方" },
];
// 已经写好的章节（主编统一维护）
window.FC_READY = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
