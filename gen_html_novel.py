import csv
import html

from collections import defaultdict

PALETTE = ["#8C3A3A", "#B4562F", "#A67C00", "#5E7B3C", "#2E6E65",
           "#31708E", "#4C5B9E", "#6E4B8E", "#8E4B6E", "#7A5230",
           "#955E4B", "#4E7A27", "#2F7B9E", "#5A63A8", "#A85A78",
           "#3E8E5A", "#C07A2E", "#546E7A", "#7B4B94", "#8C6B3E"]

NAMES = {
    10: {0: "一鵬文嫻", 1: "南京婚約", 2: None, 3: "僕傭往來", 4: "沈家長輩",
         5: "顧家眾親", 6: "曼楨與世鈞", 7: "家人親情", 8: "醫院避難", 9: "翠芝家事"},
    20: {0: "戰時通信", 1: "金芳霖生", 2: "南京親眷", 3: "曼楨蹤跡", 4: "祝家鴻才",
         5: "曼璐姊妹", 6: None, 7: "沈家長輩", 8: "僕傭往返", 9: "顧家周旋",
         10: "年節婚慶", 11: "翠芝婚後", 12: "家人親情", 13: "豫瑾來訪", 14: "世鈞叔惠",
         15: None, 16: "許太太家常", 17: "翠芝叔惠", 18: "一鵬文嫻", 19: None},
}


def esc(s):
    return html.escape(str(s), quote=True)


rows = list(csv.DictReader(open("xiaoshuo_lda_topics.csv", encoding="utf-8-sig")))

words_map = defaultdict(lambda: defaultdict(list))
docs_map = defaultdict(lambda: defaultdict(list))
for r in rows:
    nt = int(r["n_topics"])
    t = int(r["topic_id"])
    if r["type"] == "word":
        words_map[nt][t].append((r["word"], float(r["prob"])))
    else:
        docs_map[nt][t].append({
            "rank": int(r["rank"]),
            "chunk": r["doc_chunk"],
            "prob": float(r["prob"]),
            "excerpt": r["doc_excerpt"],
        })

max_prob = {nt: {t: max(w for _, w in ws) for t, ws in wm.items()} for nt, wm in words_map.items()}
scale = {nt: max(max_prob[nt].values()) for nt in words_map}

out = []
out.append("""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>《半生緣》主題模型分析 — LDA</title>
<style>
:root{
  --ink:#2b2b28; --paper:#faf7f0; --card:#fffdf8; --line:#e3ddcf;
  --accent:#2E6E65; --muted:#7a7466;
}
*{margin:0;padding:0;box-sizing:border-box}
body{
  font-family:"Noto Serif TC","Songti TC","STSong","SimSun",serif;
  background:var(--paper); color:var(--ink); line-height:1.7;
  background-image:radial-gradient(circle at 15% 10%, rgba(46,110,101,.05), transparent 40%),
                   radial-gradient(circle at 85% 90%, rgba(140,58,58,.04), transparent 40%);
}
header{padding:48px 24px 28px;text-align:center;border-bottom:3px double var(--line)}
header h1{font-size:2.1rem;letter-spacing:.3em;font-weight:700}
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
tbody tr:hover{background:#f0f5f3}
.tid{display:inline-block;min-width:52px;text-align:center;color:#fff;border-radius:6px;
     font-weight:700;padding:3px 8px;font-size:.85rem}
.tname{font-size:.88rem;color:#5c5546;margin-top:3px;letter-spacing:.06em}
.tname.none{color:#b9b2a2}
.chip{display:inline-block;margin:2px 4px 2px 0;padding:3px 10px;border-radius:16px;
      background:#fff;border:1px solid var(--line);font-size:1rem;cursor:default}
.chip small{color:var(--muted);font-size:.68rem;margin-left:3px}
.bar{height:7px;border-radius:4px;background:#e2ebe8;min-width:70px;position:relative;overflow:hidden}
.bar i{position:absolute;inset:0;border-radius:4px}
.prob{font-variant-numeric:tabular-nums;color:var(--muted);font-size:.85rem;white-space:nowrap}
.chunk{font-weight:700}
.excerpt{font-size:.88rem;max-width:560px;color:#4a463e}
td .rank{color:var(--muted);font-size:.8rem;margin-right:4px}
footer{text-align:center;color:var(--muted);font-size:.82rem;padding:30px;border-top:1px solid var(--line);letter-spacing:.1em}
</style>
</head>
<body>
<header>
  <h1>《半生緣》・主題模型分析</h1>
  <div class="sub">張愛玲　LDA (Gibbs Sampling)　jieba 分詞・每 1000 詞切成塊・剔除現代漢語停用詞（zh_sim）・100 次迭代</div>
  <div class="stats">
    <div class="stat"><b>223,431</b><span>全文字數</span></div>
    <div class="stat"><b>66</b><span>文件（1000 詞／塊）</span></div>
    <div class="stat"><b>65,493</b><span>語料詞數</span></div>
    <div class="stat"><b>12,391</b><span>詞彙表</span></div>
  </div>
</header>
<nav><a href="#m10">十主題模型</a><a href="#m20">廿主題模型</a></nav>
<main>
""")

for nt in (10, 20):
    roman = "十" if nt == 10 else "廿"
    out.append(f'<section id="m{nt}">\n<h2>{roman}主題模型</h2>')
    out.append('<div class="hint">每個主題列出機率最高的 10 個詞（括號為該詞在主題內的機率），並附 2 個最具代表性的區塊（各 1000 詞）。主題名稱為依關鍵詞與代表區塊所作之主觀解讀，無把握者標「—」。</div>')

    out.append('<h3 style="margin:0 0 12px;font-size:1.05rem;letter-spacing:.15em">一、主題關鍵詞</h3>')
    out.append('<table><thead><tr><th style="width:90px">主題</th><th style="width:120px">主題名稱</th><th>前 10 個高頻詞</th><th style="width:110px">最高詞概率</th></tr></thead><tbody>')
    for t in range(nt):
        c = PALETTE[t % len(PALETTE)]
        ws = words_map[nt][t]
        mx = max_prob[nt][t]
        name = NAMES[nt].get(t)
        ncell = f'<span class="tname">{esc(name)}</span>' if name else '<span class="tname none">—</span>'
        chips = "".join(
            f'<span class="chip" style="font-size:{0.9 + w_p / mx * 0.4:.2f}rem;border-color:{c}55">'
            f'{esc(w)}<small>{w_p:.3f}</small></span>' for w, w_p in ws)
        out.append(f'<tr><td><span class="tid" style="background:{c}">{nt}-{t}</span></td>'
                   f'<td>{ncell}</td>'
                   f'<td>{chips}</td>'
                   f'<td><div class="bar"><i style="width:{mx / scale[nt] * 100:.0f}%;background:{c}"></i></div>'
                   f'<span class="prob">{mx:.4f}</span></td></tr>')
    out.append('</tbody></table>')

    out.append('<h3 style="margin:30px 0 12px;font-size:1.05rem;letter-spacing:.15em">二、代表區塊</h3>')
    out.append('<table><thead><tr><th style="width:90px">主題</th><th style="width:34px">#</th>'
               '<th style="width:90px">區塊</th><th style="width:120px">主題概率</th><th>開頭摘錄（前 30 詞）</th></tr></thead><tbody>')
    for t in range(nt):
        c = PALETTE[t % len(PALETTE)]
        name = NAMES[nt].get(t)
        ncell = f'<div class="tname">{esc(name)}</div>' if name else '<div class="tname none">—</div>'
        for p in sorted(docs_map[nt][t], key=lambda x: x["rank"]):
            out.append(f'<tr><td><span class="tid" style="background:{c}">{nt}-{t}</span>{ncell}</td>'
                       f'<td><span class="rank">{p["rank"]}</span></td>'
                       f'<td><span class="chunk">區塊 {p["chunk"]}</span></td>'
                       f'<td><div class="bar"><i style="width:{p["prob"] * 100:.0f}%;background:{c}"></i></div>'
                       f'<span class="prob">{p["prob"]:.4f}</span></td>'
                       f'<td class="excerpt">{esc(p["excerpt"])}…</td></tr>')
    out.append('</tbody></table></section>')

out.append("""</main>
<footer>《半生緣》66 區塊 × 1000 詞・jieba 分詞・LDA（qhchina 0.2.7）　|　語料：qhchina-data 中文小說100強 (mcjkurz)</footer>
</body></html>""")

with open("xiaoshuo_lda_report.html", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("已生成: xiaoshuo_lda_report.html")
