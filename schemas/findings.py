from pydantic import BaseModel

class Fact(BaseModel):
    statement: str
    sources:list[str]

class Finding(BaseModel):
    topic: str
    facts: list[Fact]