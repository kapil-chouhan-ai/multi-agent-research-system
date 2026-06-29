import json
import os
import numpy as np

from schemas.state import AgentState


class ResearchMemoryStore:
    """Persists finished AgentStates across runs so a repeated/similar query
    can be served from a prior report instead of re-running the whole
    pipeline (V4 roadmap item: "reuse prior findings for related queries").

    Plain JSON file, not a database -- this is a single-user CLI project,
    a JSON list is sufficient and keeps the diff to the rest of the repo
    small. Similarity is cosine distance over the same embedding_model
    already used for dense retrieval (no new dependency); falls back to
    exact-match if no embedding_model is supplied.
    """

    def __init__(self, path: str = "memory/research_history.json", embedding_model=None, similarity_threshold: float = 0.86):
        self.path = path
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        self._records = self._load()

    def _load(self) -> list[dict]:
        if not os.path.exists(self.path):
            return []
        with open(self.path, "r") as f:
            return json.load(f)

    def _save_to_disk(self) -> None:
        with open(self.path, "w") as f:
            json.dump(self._records, f, indent=2)

    def find_similar(self, query: str) -> AgentState | None:
        if not self._records:
            return None

        if self.embedding_model is None:
            for record in self._records:
                if record["query"].strip().lower() == query.strip().lower():
                    return AgentState.model_validate(record["state"])
            return None

        query_emb = np.array(self.embedding_model.encode([query])[0], dtype=np.float32)
        query_emb /= (np.linalg.norm(query_emb) + 1e-8)

        best_score, best_record = -1.0, None
        for record in self._records:
            stored_emb = np.array(record["embedding"], dtype=np.float32)
            score = float(np.dot(query_emb, stored_emb))
            if score > best_score:
                best_score, best_record = score, record

        if best_record is not None and best_score >= self.similarity_threshold:
            return AgentState.model_validate(best_record["state"])
        return None

    def save(self, query: str, state: AgentState) -> None:
        record = {"query": query, "state": state.model_dump(mode="json")}
        # if self.embedding_model is not None:
        #     # emb = np.array(self.embedding_model.encode([query])[0], dtype=np.float32)
        #     # emb /= (np.linalg.norm(emb) + 1e-8)
        #     # record["embedding"] = emb.tolist()
        self._records.append(record)
        self._save_to_disk()
