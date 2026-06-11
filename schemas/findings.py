from pydantic import BaseModel

class Facts(BaseModel):
    statement: str
    sources:list[str]

class Finding(BaseModel):
    topic: str
    facts: list[Facts]