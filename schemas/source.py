from typing import Optional
from pydantic import BaseModel

class Source(BaseModel):
    url: str
    domain: Optional[str] = None