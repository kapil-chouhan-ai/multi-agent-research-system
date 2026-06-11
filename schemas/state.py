from pydantic import BaseModel, Field

from schemas.plan import Plan
from schemas.findings import Finding
from schemas.report import Report

class AgentState(BaseModel):
    query: str | None = None
    plan: Plan | None = None
    findings: list[Finding] = Field(default_factory= list)
    report: Report | None = None
