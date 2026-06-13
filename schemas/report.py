from pydantic import BaseModel

class ReportSection(BaseModel):
    topic: str
    content: str
    sources: list[str]

class Report(BaseModel):
    title: str
    summary: str
    sections: list[ReportSection]
