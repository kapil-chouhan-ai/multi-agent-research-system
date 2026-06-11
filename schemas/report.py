from pydantic import BaseModel

class Report(BaseModel):
    title: str
    summary: str
