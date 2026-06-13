from schemas.corpus import ResearchCorpus
from schemas.retrieval import RetrievalResult
import faiss
import numpy as np

class RetrieverNode:
    def __init__(self, embedding_model, top_k: int = 5):
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

    def retrieve(self, topic: str) -> RetrievalResult:
        topic_embs = np.array(self.embedding_model.encode([topic]), dtype = np.float32)
        faiss.normalize_L2(topic_embs)

        D, I = self.index.search(topic_embs, self.top_k)

        retrieved_chunks = []
        retrieval_scores = []

        for index, distance in zip(I[0], D[0]):
            retrieved_chunks.append(self.chunks[index])
            retrieval_scores.append(float(distance))
        

        return RetrievalResult(
            topic = topic,
            retrieved_chunks= retrieved_chunks,
            retrieval_scores = retrieval_scores
        )
