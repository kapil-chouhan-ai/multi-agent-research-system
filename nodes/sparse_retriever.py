from rank_bm25 import BM25Okapi

from schemas.corpus import ResearchCorpus
from schemas.retrieval import RetrievalResult


def _tokenize(text: str) -> list[str]:
    return text.lower().split()


class SparseRetrieverNode:
    """BM25 lexical retriever over the same chunk corpus the dense
    RetrieverNode operates on. Kept as a standalone node (not folded into
    RetrieverNode) so eval/benchmark.py can score dense-only vs sparse-only
    vs hybrid in isolation.
    """

    def __init__(self, top_k: int = 5):
        self.top_k = top_k
        self.chunks = None
        self.bm25 = None

    def build(self, corpus: ResearchCorpus) -> None:
        self.chunks = corpus.chunks
        tokenized = [_tokenize(chunk.content) for chunk in self.chunks]
        self.bm25 = BM25Okapi(tokenized)

    def ranked_indices(self, topic: str, top_k: int | None = None) -> list[tuple[int, float]]:
        """Returns (chunk_index, bm25_score) sorted best-first. Used directly
        by HybridRetrieverNode for fusion; exposed publicly for the eval harness.
        """
        k = top_k or self.top_k
        scores = self.bm25.get_scores(_tokenize(topic))
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [(i, float(scores[i])) for i in ranked]

    def retrieve(self, topic: str) -> RetrievalResult:
        ranked = self.ranked_indices(topic)
        return RetrievalResult(
            topic=topic,
            retrieved_chunks=[self.chunks[i] for i, _ in ranked],
            retrieval_scores=[s for _, s in ranked],
        )
