from pydantic import BaseModel, Field


class StoryboardShot(BaseModel):
    shot_number: int

    shot_type: str = ""

    camera_move: str = ""

    lens: str = ""

    framing: str = ""

    duration: float = 0.0

    prompt: str = ""

    narration: str = ""

    sound_effects: list[str] = Field(default_factory=list)

    notes: str = ""


class StoryboardScene(BaseModel):
    scene_number: int

    title: str = ""

    shots: list[StoryboardShot] = Field(default_factory=list)


class StoryboardData(BaseModel):
    scenes: list[StoryboardScene] = Field(default_factory=list)