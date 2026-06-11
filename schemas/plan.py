from pydantic import BaseModel

class Plan(BaseModel):
    user_query: str
    research_points: list[str] 