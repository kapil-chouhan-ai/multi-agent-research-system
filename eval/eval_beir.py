"""
Run with (from repo root, after `pip install -r requirements.txt`):

    python -m eval.evaluate_beir --datasets scifact nfcorpus fiqa --total-queries 500

First run downloads each dataset from the official BEIR host into
eval/datasets/{name}/ (~10MB-500MB depending on dataset -- fiqa's corpus is
the big one). Needs network access to public.ukp.informatik.tu-darmstadt.de
and to huggingface.co (for the embedding model / reranker checkpoints) --
neither is reachable from a sandboxed environment, run this on your machine.

Metrics use pytrec_eval (pip install pytrec-eval-terrier, imports as
pytrec_eval) -- the same library BEIR's own EvaluateRetrieval.evaluate()
uses, so NDCG@10 / Recall@100 here are directly comparable to published
BEIR leaderboard numbers, not a custom metric that merely looks similar.
"""

import argparse
import json
import os
import time

import pytrec_eval

from schemas.chunk import Chunk
from schemas.corpus import ResearchCorpus
from nodes.retriever import RetrieverNode
from nodes.sparse_retriever import SparseRetrieverNode
from nodes.hybrid_retriever import HybridRetrieverNode

from eval.beir_loader import load_beir_dataset, sample_queries

EVAL_DIR = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(EVAL_DIR, "datasets")
RESULTS_DIR = os.path.join(EVAL_DIR, "results")
K_VALUES = [1, 3, 5, 10, 100]


def pytrec_evaluate(qrels: dict, results: dict, k_values: list[int]) -> dict:
    """Adapted from beir.retrieval.evaluation.EvaluateRetrieval.evaluate()
    (github.com/beir-cellar/beir) -- reimplemented directly against
    pytrec_eval here instead of depending on the full beir package, since
    we already have our own retriever nodes.
    """
    ndcg_s = "ndcg_cut." + ",".join(str(k) for k in k_values)
    map_s = "map_cut." + ",".join(str(k) for k in k_values)
    recall_s = "recall." + ",".join(str(k) for k in k_values)
    p_s = "P." + ",".join(str(k) for k in k_values)

    evaluator = pytrec_eval.RelevanceEvaluator(qrels, {ndcg_s, map_s, recall_s, p_s})
    scores = evaluator.evaluate(results)

    out = {f"{m}@{k}": 0.0 for m in ("NDCG", "MAP", "Recall", "P") for k in k_values}
    n = max(len(scores), 1)
    for qid_scores in scores.values():
        for k in k_values:
            out[f"NDCG@{k}"] += qid_scores[f"ndcg_cut_{k}"]
            out[f"MAP@{k}"] += qid_scores[f"map_cut_{k}"]
            out[f"Recall@{k}"] += qid_scores[f"recall_{k}"]
            out[f"P@{k}"] += qid_scores[f"P_{k}"]
    return {k: round(v / n, 5) for k, v in out.items()}


def build_chunks(corpus: dict) -> list[Chunk]:
    return [
        Chunk(chunk_id=doc_id, url=doc_id, content=f"{doc.get('title', '')} {doc['text']}".strip())
        for doc_id, doc in corpus.items()
    ]


def retrieve_all(retriever_fn, queries: dict, top_k: int) -> dict:
    """retriever_fn(query_text, top_k) -> RetrievalResult. Returns
    {qid: {doc_id: score}} in the shape pytrec_eval expects."""
    results = {}
    for qid, text in queries.items():
        r = retriever_fn(text, top_k)
        results[qid] = {chunk.chunk_id: score for chunk, score in zip(r.retrieved_chunks, r.retrieval_scores)}
    return results


def evaluate_dataset(
    name: str,
    embedding_model,
    reranker=None,
    total_queries_target: int = 167,
    pool_size: int = 100,
    rerank_pool: int = 100,
    k_values: list[int] = K_VALUES,
) -> dict:
    print(f"\n=== {name} ===")
    corpus, queries, qrels = load_beir_dataset(name, DATASETS_DIR)
    queries, qrels = sample_queries(queries, qrels, n=total_queries_target)
    print(f"corpus={len(corpus)} docs, evaluating on {len(queries)} sampled queries")

    chunks = build_chunks(corpus)
    research_corpus = ResearchCorpus(chunks=chunks)
    max_k = max(k_values)

    dense = RetrieverNode(embedding_model=embedding_model, top_k=max_k)
    dense.build(research_corpus)
    sparse = SparseRetrieverNode(top_k=max_k)
    sparse.build(research_corpus)
    hybrid = HybridRetrieverNode(embedding_model=embedding_model, top_k=max_k, pool_size=pool_size)
    hybrid.build(research_corpus)

    variants = {
        "dense": lambda q, k: dense.retrieve(q),
        "sparse": lambda q, k: sparse.retrieve(q),
        "hybrid": lambda q, k: hybrid.retrieve(q),
    }
    if reranker is not None:
        variants["hybrid+rerank"] = lambda q, k: reranker.rerank(
            hybrid.retrieve(q, top_k=min(rerank_pool, len(chunks))), top_n=max_k
        )

    dataset_results = {"dataset": name, "n_docs": len(corpus), "n_queries": len(queries), "variants": {}}

    headline_ndcg_k = 10 if 10 in k_values else max(k_values)
    headline_recall_k = 100 if 100 in k_values else max(k_values)

    for variant_name, fn in variants.items():
        start = time.time()
        results = retrieve_all(fn, queries, max_k)
        metrics = pytrec_evaluate(qrels, results, k_values)
        metrics["latency_sec_total"] = round(time.time() - start, 2)
        dataset_results["variants"][variant_name] = metrics
        ndcg_key, recall_key = f"NDCG@{headline_ndcg_k}", f"Recall@{headline_recall_k}"
        print(f"  {variant_name:<16} {ndcg_key}={metrics[ndcg_key]}  {recall_key}={metrics[recall_key]}")

    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_path = os.path.join(RESULTS_DIR, f"{name}.json")
    with open(out_path, "w") as f:
        json.dump(dataset_results, f, indent=2)

    return dataset_results


def write_summary(all_results: list[dict]) -> None:
    lines = ["# BEIR Retrieval Benchmark Summary\n"]
    for res in all_results:
        sample_metrics = next(iter(res["variants"].values()))
        available_ks = sorted({int(k.split("@")[1]) for k in sample_metrics if k.startswith("NDCG@")})
        k = 10 if 10 in available_ks else max(available_ks)

        lines.append(f"\n## {res['dataset']}  ({res['n_docs']} docs, {res['n_queries']} queries)\n")
        lines.append(f"| variant | NDCG@{k} | Recall@{k} | MAP@{k} | P@{k} |")
        lines.append("|---|---|---|---|---|")
        for variant, m in res["variants"].items():
            lines.append(f"| {variant} | {m[f'NDCG@{k}']} | {m[f'Recall@{k}']} | {m[f'MAP@{k}']} | {m[f'P@{k}']} |")
    with open(os.path.join(RESULTS_DIR, "summary.md"), "w") as f:
        f.write("\n".join(lines) + "\n")


def main(dataset_names: list[str], total_queries: int, use_rerank: bool):
    from sentence_transformers import SentenceTransformer

    embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    reranker = None
    if use_rerank:
        from nodes.reranker import RerankerNode
        reranker = RerankerNode()

    per_dataset = max(1, total_queries // len(dataset_names))
    all_results = [
        evaluate_dataset(name, embedding_model, reranker=reranker, total_queries_target=per_dataset)
        for name in dataset_names
    ]
    write_summary(all_results)
    print(f"\nWrote eval/results/{{{','.join(dataset_names)}}}.json and eval/results/summary.md")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", nargs="+", default=["scifact", "nfcorpus", "fiqa"])
    parser.add_argument("--total-queries", type=int, default=500, help="split roughly evenly across --datasets")
    parser.add_argument("--no-rerank", action="store_true", help="skip the cross-encoder variant (slow on CPU at scale)")
    args = parser.parse_args()
    main(args.datasets, args.total_queries, use_rerank=not args.no_rerank)