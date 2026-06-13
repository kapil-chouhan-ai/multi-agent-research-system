from schemas.page import Page
from pydantic import BaseModel
from schemas.source import Source

class PageReaderResult(BaseModel):
    pages: list[Page]
    failed_sources: list[Source]