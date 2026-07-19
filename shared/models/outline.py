from pydantic import BaseModel, Field


class OutlineScene(BaseModel):

    scene: int

    title: str

    goal: str

    duration: int

    key_points: list[str] = Field(default_factory=list)

    visual_focus: str = ""

    emotional_tone: str = ""

    transition: str = ""


class OutlineData(BaseModel):

    title: str = ""

    scene_count: int = 0

    total_duration: int = 0

    scenes: list[OutlineScene] = Field(default_factory=list)