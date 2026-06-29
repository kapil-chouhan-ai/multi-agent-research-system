from schemas.corpus import ResearchCorpus
from schemas.retrieval import RetrievalResult
import faiss
import numpy as np

class RetrieverNode:
    def __init__(self, embedding_model, top_k: int = 10):
        self.embedding_model = embedding_model
        self.top_k = top_k

        self.chunks = None
        self.embeddings = None
        self.index = None

    def build(self, corpus: ResearchCorpus) -> None:
        self.chunks = corpus.chunks

        text = [chunk.content for chunk in self.chunks]

        self.embeddings = (self.embedding_model.encode(text))
        faiss.normalize_L2(self.embeddings)

        d = self.embeddings.shape[1]

        self.index = faiss.IndexFlatIP(d)
        self.index.add(self.embeddings)

    def ranked_indices(self, topic: str, top_k: int | None = None) -> list[tuple[int, float]]:
        """Returns (chunk_index, cosine_score) sorted best-first, skipping the
        -1 padding FAISS returns when the index has fewer than top_k vectors.
        Used by HybridRetrieverNode for fusion and by eval/benchmark.py.
        """
        k = top_k or self.top_k
        topic_embs = np.array(self.embedding_model.encode([topic]), dtype=np.float32)
        faiss.normalize_L2(topic_embs)

        D, I = self.index.search(topic_embs, k)

        return [
            (int(idx), float(score))
            for idx, score in zip(I[0], D[0])
            if idx != -1
        ]

    def retrieve(self, topic: str) -> RetrievalResult:
        ranked = self.ranked_indices(topic)

        return RetrievalResult(
            topic=topic,
            retrieved_chunks=[self.chunks[i] for i, _ in ranked],
            retrieval_scores=[s for _, s in ranked],
        )
