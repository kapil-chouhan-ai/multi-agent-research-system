from pydantic import BaseModel

class Plan(BaseModel):
    main_topic: str
    research_points: list[str]

class SearchQueries(BaseModel):
    topic: str
    queries: list[str]