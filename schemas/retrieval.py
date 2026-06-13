from pydantic import BaseModel
from schemas.chunk import Chunk
from typing import Optional

class RetrievalResult(BaseModel):
    topic: str
    retrieved_chunks: list[Chunk]
    retrieval_scores: Optional[list[float]] |None = None