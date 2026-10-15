import csv
import html
import re

from collections import defaultdict

PALETTE = ["#8C3A3A", "#B4562F", "#A67C00", "#5E7B3C", "#2E6E65",
           "#31708E", "#4C5B9E", "#6E4B8E", "#8E4B6E", "#7A5230",
           "#955E4B", "#4E7A27", "#2F7B9E", "#5A63A8", "#A85A78",
           "#3E8E5A", "#C07A2E", "#546E7A", "#7B4B94", "#8C6B3E"]

NAMES = {
    10: {0: None, 1: "春日花酒", 2: "江湖行旅", 3: "朝廷文事", 4: "風光清景",
         5: "祭祀樂歌", 6: "宮閨豔情", 7: "征戍行旅", 8: "山林閒隱", 9: "人生說理"},
    20: {0: "送別懷人", 1: "仕宦文名", 2: "豔情閨閣", 3: "山林泉石", 4: "飲酒流年",
         5: "春柳離愁", 6: "學道說理", 7: "遊仙求道", 8: "登高攬勝", 9: "秋寒草木",
         10: "應制宮苑", 11: "騷體古歌", 12: "郊廟頌德", 13: "邊塞征戰", 14: "秋夜寒月",
         15: "禪寺僧吟", 16: "江湖舟行", 17: "老病身世", 18: None, 19: "歸途行旅"},
}


def topic_name(nt, t):
    return NAMES[nt].get(t) or "—（未命名）"


def esc(s):
    return html.escape(str(s), quote=True)


def clean_text(t):
    t = re.sub(r"第\d+页", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def poem_lines(t):
    parts = re.split(r"(?<=[。？！])\s*", clean_text(t))
    return "<br>".join(p for p in (x.strip() for x in parts) if p)


rows = list(csv.DictReader(open("全唐诗_lda_topics_sw.csv", encoding="utf-8-sig")))

chars = defaultdict(lambda: defaultdict(list))
poems = defaultdict(lambda: defaultdict(list))
for r in rows:
    nt = int(r["n_topics"])
    t = int(r["topic_id"])
    if r["type"] == "char":
        chars[nt][t].append((r["char"], float(r["prob"])))
    else:
        poems[nt][t].append({
            "rank": int(r["rank"]),
            "title": r["poem_title"] or "無題",
            "author": r["poem_author"] or "佚名",
            "prob": float(r["prob"]),
            "text": r["poem_text"],
        })

max_prob = {nt: {t: max(w for _, w in words) for t, words in cs.items()} for nt, cs in chars.items()}

out = []
out.append("""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>全唐詩主題模型分析 — LDA（停用詞版）</title>
<style>
:root{
  --ink:#2b2b28; --paper:#faf7f0; --card:#fffdf8; --line:#e3ddcf;
  --accent:#8C3A3A; --muted:#7a7466;
}
*{margin:0;padding:0;box-sizing:border-box}
body{
  font-family:"Noto Serif TC","Songti TC","STSong","SimSun",serif;
  background:var(--paper); color:var(--ink); line-height:1.7;
  background-image:radial-gradient(circle at 15% 10%, rgba(140,58,58,.04), transparent 40%),
                   radial-gradient(circle at 85% 90%, rgba(46,110,101,.05), transparent 40%);
}
header{padding:48px 24px 28px;text-align:center;border-bottom:3px double var(--line)}
header h1{font-size:2.1rem;letter-spacing:.35em;font-weight:700}
header .sub{color:var(--muted);margin-top:10px;font-size:.95rem;letter-spacing:.12em}
.stats{display:flex;justify-content:center;gap:14px;flex-wrap:wrap;margin-top:22px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 22px;text-align:center}
.stat b{display:block;font-size:1.35rem;color:var(--accent)}
.stat span{font-size:.8rem;color:var(--muted);letter-spacing:.08em}
nav{position:sticky;top:0;z-index:10;background:rgba(250,247,240,.94);backdrop-filter:blur(6px);
    border-bottom:1px solid var(--line);display:flex;justify-content:center;gap:8px;padding:10px}
nav a{color:var(--ink);text-decoration:none;padding:6px 18px;border-radius:20px;font-size:.92rem;border:1px solid transparent}
nav a:hover{border-color:var(--accent);color:var(--accent)}
main{max-width:1180px;margin:0 auto;padding:34px 20px 80px}
section{margin-bottom:70px}
h2{font-size:1.45rem;letter-spacing:.2em;margin-bottom:6px;display:flex;align-items:center;gap:12px}
h2::after{content:"";flex:1;height:1px;background:var(--line)}
.hint{color:var(--muted);font-size:.88rem;margin-bottom:20px}
table{width:100%;border-collapse:collapse;background:var(--card);
      border:1px solid var(--line);border-radius:12px;overflow:hidden;
      box-shadow:0 2px 10px rgba(60,50,30,.06);font-size:.95rem}
th,td{padding:11px 14px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
thead th{background:#f1ece0;font-size:.85rem;letter-spacing:.15em;color:#5c5546;
         border-bottom:2px solid var(--line);white-space:nowrap}
tbody tr:last-child td{border-bottom:none}
tbody tr:hover{background:#faf5e9}
.tid{display:inline-block;min-width:52px;text-align:center;color:#fff;border-radius:6px;
     font-weight:700;padding:3px 8px;font-size:.85rem}
.tname{font-size:.88rem;color:#5c5546;margin-top:3px;letter-spacing:.06em}
.tname.none{color:#b9b2a2}
.chip{display:inline-block;margin:2px 4px 2px 0;padding:3px 10px;border-radius:16px;
      background:#fff;border:1px solid var(--line);font-size:1.02rem;cursor:default}
.chip small{color:var(--muted);font-size:.68rem;margin-left:3px}
.bar{height:7px;border-radius:4px;background:#eee7d8;min-width:70px;position:relative;overflow:hidden}
.bar i{position:absolute;inset:0;border-radius:4px}
.prob{font-variant-numeric:tabular-nums;color:var(--muted);font-size:.85rem;white-space:nowrap}
.ptitle{font-weight:700}
.pauthor{color:var(--muted)}
.ptext{font-size:.9rem;max-width:520px}
td .rank{color:var(--muted);font-size:.8rem;margin-right:4px}
footer{text-align:center;color:var(--muted);font-size:.82rem;padding:30px;border-top:1px solid var(--line);letter-spacing:.1em}
</style>
</head>
<body>
<header>
  <h1>全唐詩・主題模型分析</h1>
  <div class="sub">LDA (Gibbs Sampling)　以字為單位・標點刪除・剔除文言停用詞（zh_cl_sim）・100 次迭代</div>
  <div class="stats">
    <div class="stat"><b>45,725</b><span>詩作文件</span></div>
    <div class="stat"><b>258.9 萬</b><span>總字數</span></div>
    <div class="stat"><b>7,523</b><span>詞彙表</span></div>
    <div class="stat"><b>2</b><span>模型（10/20 主題）</span></div>
  </div>
</header>
<nav><a href="#m10">十主題模型</a><a href="#m20">廿主題模型</a></nav>
<main>
""")

for nt in (10, 20):
    roman = "十" if nt == 10 else "廿"
    out.append(f'<section id="m{nt}">\n<h2>{roman}主題模型</h2>')
    out.append(f'<div class="hint">每個主題列出機率最高的 10 個字（括號為該字在主題內的機率），並附 2 首最具代表性的詩。主題名稱為依關鍵字與代表詩所作之主觀解讀，無把握者標「—」。</div>')

    out.append('<h3 style="margin:0 0 12px;font-size:1.05rem;letter-spacing:.15em">一、主題關鍵字</h3>')
    out.append('<table><thead><tr><th style="width:90px">主題</th><th style="width:120px">主題名稱</th><th>前 10 個高頻字</th><th style="width:110px">最高字概率</th></tr></thead><tbody>')
    for t in range(nt):
        c = PALETTE[t % len(PALETTE)]
        words = chars[nt][t]
        mx = max_prob[nt][t]
        name = NAMES[nt].get(t)
        ncell = f'<span class="tname">{esc(name)}</span>' if name else '<span class="tname none">—</span>'
        chips = "".join(
            f'<span class="chip" style="font-size:{0.95 + w / mx * 0.5:.2f}rem;border-color:{c}55">'
            f'{esc(ch)}<small>{w:.3f}</small></span>' for ch, w in words)
        out.append(f'<tr><td><span class="tid" style="background:{c}">{nt}-{t}</span></td>'
                   f'<td>{ncell}</td>'
                   f'<td>{chips}</td>'
                   f'<td><div class="bar"><i style="width:{mx * 100 / 0.05:.0f}%;background:{c}"></i></div>'
                   f'<span class="prob">{mx:.4f}</span></td></tr>')
    out.append('</tbody></table>')

    out.append('<h3 style="margin:30px 0 12px;font-size:1.05rem;letter-spacing:.15em">二、代表詩作</h3>')
    out.append('<table><thead><tr><th style="width:90px">主題</th><th style="width:34px">#</th>'
               '<th style="width:200px">詩題／作者</th><th style="width:120px">主題概率</th><th>詩文</th></tr></thead><tbody>')
    for t in range(nt):
        c = PALETTE[t % len(PALETTE)]
        name = NAMES[nt].get(t)
        ncell = f'<div class="tname">{esc(name)}</div>' if name else '<div class="tname none">—</div>'
        for p in sorted(poems[nt][t], key=lambda x: x["rank"]):
            out.append(f'<tr><td><span class="tid" style="background:{c}">{nt}-{t}</span>{ncell}</td>'
                       f'<td><span class="rank">{p["rank"]}</span></td>'
                       f'<td><div class="ptitle">{esc(p["title"])}</div><div class="pauthor">{esc(p["author"])}</div></td>'
                       f'<td><div class="bar"><i style="width:{p["prob"] * 100:.0f}%;background:{c}"></i></div>'
                       f'<span class="prob">{p["prob"]:.4f}</span></td>'
                       f'<td class="ptext">{poem_lines(p["text"])}</td></tr>')
    out.append('</tbody></table></section>')

out.append("""</main>
<footer>全唐詩 45,725 首・字元級 LDA・qhchina 0.2.7　|　數據：qhchina-data (mcjkurz)</footer>
</body></html>""")

with open("全唐诗_lda_report_sw.html", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("已生成: 全唐诗_lda_report_sw.html")
