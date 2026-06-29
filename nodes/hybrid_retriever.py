from schemas.corpus import ResearchCorpus
from schemas.retrieval import RetrievalResult

from nodes.retriever import RetrieverNode
from nodes.sparse_retriever import SparseRetrieverNode


class HybridRetrieverNode:
    """Fuses dense (FAISS cosine) and sparse (BM25) rankings with
    Reciprocal Rank Fusion. RRF is used over weighted score-sum because
    FAISS cosine scores and BM25 scores live on incomparable scales --
    fusing by rank avoids having to invent a normalization.

    RRF formula: score(chunk) = sum_r 1 / (k_rrf + rank_r(chunk))
    where rank_r is 1-indexed rank in retriever r's ranked list, and a
    chunk missing from a retriever's list contributes 0 for that retriever.
    """

    def __init__(self, embedding_model, top_k: int = 5, pool_size: int = 20, k_rrf: int = 60):
        self.dense = RetrieverNode(embedding_model=embedding_model, top_k=pool_size)
        self.sparse = SparseRetrieverNode(top_k=pool_size)
        self.top_k = top_k
        self.pool_size = pool_size
        self.k_rrf = k_rrf
        self.chunks = None

    def build(self, corpus: ResearchCorpus) -> None:
        self.chunks = corpus.chunks
        self.dense.build(corpus)
        self.sparse.build(corpus)

    def retrieve(self, topic: str, top_k: int | None = None) -> RetrievalResult:
        k = top_k or self.top_k

        dense_ranked = self.dense.ranked_indices(topic, top_k=self.pool_size)
        sparse_ranked = self.sparse.ranked_indices(topic, top_k=self.pool_size)

        fused_scores: dict[int, float] = {}
        for rank, (idx, _) in enumerate(dense_ranked, start=1):
            fused_scores[idx] = fused_scores.get(idx, 0.0) + 1.0 / (self.k_rrf + rank)
        for rank, (idx, _) in enumerate(sparse_ranked, start=1):
            fused_scores[idx] = fused_scores.get(idx, 0.0) + 1.0 / (self.k_rrf + rank)

        fused = sorted(fused_scores.items(), key=lambda kv: kv[1], reverse=True)[:k]

        return RetrievalResult(
            topic=topic,
            retrieved_chunks=[self.chunks[i] for i, _ in fused],
            retrieval_scores=[s for _, s in fused],
        )
