from pydantic import BaseModel
from schemas.chunk import Chunk

class ResearchCorpus(BaseModel):
    chunks: list[Chunk]