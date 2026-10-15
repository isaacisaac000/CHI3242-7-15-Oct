import csv
import re

import jieba
from qhchina.analytics.topicmodels import LDAGibbsSampler
from qhchina.helpers import load_stopwords

NOVEL_FILES = ["24_半生缘.txt"]
CHUNK_SIZE = 1000
N_TOPICS_LIST = (10, 20)
ITERATIONS = 100
RANDOM_STATE = 42
MIN_CHUNK = 100
CJK = re.compile(r"[\u4e00-\u9fff]")

STOPWORDS = load_stopwords("zh_sim")
print(f"停用詞（zh_sim 現代漢語）: {len(STOPWORDS)} 個")


def read_novel(path):
    with open(path, encoding="utf-8-sig") as f:
        return f.read()


def tokenize(text):
    words = []
    for w in jieba.cut(text):
        w = w.strip()
        if not w or not CJK.search(w):
            continue
        if w in STOPWORDS:
            continue
        words.append(w)
    return words


def chunk_novel(text):
    words = tokenize(text)
    n_chunks = len(words) // CHUNK_SIZE
    chunks = []
    for i in range(n_chunks + 1):
        part = words[i * CHUNK_SIZE:(i + 1) * CHUNK_SIZE]
        if len(part) >= MIN_CHUNK:
            chunks.append(part)
    return chunks


def main():
    docs = []
    meta = []
    for path in NOVEL_FILES:
        text = read_novel(path)
        chunks = chunk_novel(text)
        print(f"{path}: {len(text)} 字 → 分詞後切成 {len(chunks)} 個 1000 詞區塊")
        for j, ch in enumerate(chunks):
            docs.append(ch)
            meta.append({"file": path, "chunk": j + 1,
                         "excerpt": " ".join(ch[:20])})

    print(f"總文件數: {len(docs)}, 總詞數: {sum(len(d) for d in docs)}")

    results = []
    for n_topics in N_TOPICS_LIST:
        print(f"\n=== 訓練 {n_topics} 主題模型 ===")
        model = LDAGibbsSampler(n_topics=n_topics, iterations=ITERATIONS,
                                random_state=RANDOM_STATE)
        model.fit(docs)
        for t in range(n_topics):
            words = model.get_topic_words(t, n_words=10)
            top_docs = model.get_top_documents(t, n_docs=2)
            reps = []
            for doc_id, prob in top_docs:
                reps.append({**meta[doc_id], "prob": prob,
                             "excerpt": " ".join(docs[doc_id][:30])})
            results.append({"n_topics": n_topics, "topic_id": t,
                            "chars": words, "poems": reps})

    out_csv = "xiaoshuo_lda_topics.csv"
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["n_topics", "topic_id", "rank", "type", "word", "prob",
                    "doc_file", "doc_chunk", "doc_excerpt"])
        for r in results:
            for rank, (word, prob) in enumerate(r["chars"], 1):
                w.writerow([r["n_topics"], r["topic_id"], rank, "word", word,
                            f"{prob:.4f}", "", "", ""])
            for rank, p in enumerate(r["poems"], 1):
                w.writerow([r["n_topics"], r["topic_id"], rank, "doc", "",
                            f"{p['prob']:.4f}", p["file"], p["chunk"], p["excerpt"]])

    print(f"\n已儲存: {out_csv}")
    for r in results:
        nt = r["n_topics"]
        if r["topic_id"] == 0:
            print(f"\n===== {nt} 主題 =====")
        words_str = " ".join(f"{w}({p:.3f})" for w, p in r["chars"])
        print(f"主題{r['topic_id']}: {words_str}")
        for p in r["poems"]:
            print(f"   [{p['file']} 區塊{p['chunk']} | p={p['prob']:.4f}] {p['excerpt']}…")


if __name__ == "__main__":
    main()
