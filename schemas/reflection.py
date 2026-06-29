from typing import Optional
from pydantic import BaseModel


class Reflection(BaseModel):
    sufficient: bool
    reason: str
    refined_query: Optional[str] = None
