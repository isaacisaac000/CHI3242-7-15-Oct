import csv
import json
import re

from qhchina.analytics.topicmodels import LDAGibbsSampler
from qhchina.helpers import load_stopwords

STOPWORDS = load_stopwords("zh_cl_sim")
print(f"停用詞（zh_cl_sim）: {len(STOPWORDS)} 個")

CJK = re.compile(r"[\u4e00-\u9fff]")

with open("全唐诗.json", encoding="utf-8") as f:
    data = json.load(f)

docs = []
idx_map = []
for i, p in enumerate(data):
    chars = CJK.findall("".join(p.get("paragraphs", [])))
    if len(chars) >= 4:
        docs.append(chars)
        idx_map.append(i)

print(f"總詩數: {len(data)}, 有效文件: {len(docs)}, 總字數: {sum(len(d) for d in docs)}")

results = []
for n_topics in (10, 20):
    print(f"\n=== 訓練 {n_topics} 主題模型 ===")
    model = LDAGibbsSampler(n_topics=n_topics, iterations=100, random_state=42, stopwords=STOPWORDS)
    model.fit(docs)
    for t in range(n_topics):
        words = model.get_topic_words(t, n_words=10)
        top_docs = model.get_top_documents(t, n_docs=2)
        poems = []
        for doc_id, prob in top_docs:
            p = data[idx_map[doc_id]]
            poems.append({
                "title": p.get("title", ""),
                "author": p.get("author", ""),
                "prob": prob,
                "text": "".join(p.get("paragraphs", [])),
            })
        results.append({
            "n_topics": n_topics,
            "topic_id": t,
            "chars": words,
            "poems": poems,
        })

with open("全唐诗_lda_topics_sw.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["n_topics", "topic_id", "rank", "type", "char", "prob",
                "poem_title", "poem_author", "poem_text"])
    for r in results:
        for rank, (ch, prob) in enumerate(r["chars"], 1):
            w.writerow([r["n_topics"], r["topic_id"], rank, "char", ch, f"{prob:.4f}", "", "", ""])
        for rank, p in enumerate(r["poems"], 1):
            w.writerow([r["n_topics"], r["topic_id"], rank, "poem", "", f"{p['prob']:.4f}",
                        p["title"], p["author"], p["text"]])

print("\n已儲存: 全唐诗_lda_topics_sw.csv")
