from typing import Optional
from pydantic import BaseModel

class Page(BaseModel):
    url: str
    content: str
    title: Optional[str] = None