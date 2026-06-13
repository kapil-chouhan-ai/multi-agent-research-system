from pydantic import BaseModel

class Chunk(BaseModel):
    chunk_id: str
    url: str
    content:str