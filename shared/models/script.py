from pydantic import BaseModel, Field


class ScriptScene(BaseModel):

    scene: int

    title: str

    narration: str

    visual_description: str

    duration: int


class ScriptData(BaseModel):

    scenes: list[ScriptScene] = Field(default_factory=list)