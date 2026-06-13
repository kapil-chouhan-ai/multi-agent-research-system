from pydantic import BaseModel

class Plan(BaseModel):
    main_topic: str
    research_points: list[str]