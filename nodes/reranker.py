from sentence_transformers import CrossEncoder
from schemas.retrieval import RetrievalResult

class RerankerNode:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2", top_n: int = 5):
        self.model = CrossEncoder(model_name)
        self.top_n = top_n

    def rerank(self, retrieval_result: RetrievalResult, top_n: int | None = None) -> RetrievalResult:
        n = top_n or self.top_n
        chunks = retrieval_result.retrieved_chunks

        if not chunks:
            return retrieval_result

        pairs = [(retrieval_result.topic, chunk.content) for chunk in chunks]
        scores = self.model.predict(pairs)

        order = sorted(range(len(chunks)), key=lambda i: scores[i], reverse=True)[:n]

        return RetrievalResult(
            topic=retrieval_result.topic,
            retrieved_chunks=[chunks[i] for i in order],
            retrieval_scores=[float(scores[i]) for i in order],
        )
