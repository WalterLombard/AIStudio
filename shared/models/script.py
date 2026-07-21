"""
AIStudio Script Models

Defines the documentary script produced by the Script Agent.

Author : AIStudio
"""

from pydantic import BaseModel, Field


class ScriptLine(BaseModel):
    """
    A single narration block within a documentary scene.
    """

    order: int

    narration: str

    visual_description: str = ""

    duration: int


class ScriptScene(BaseModel):
    """
    One completed documentary scene.
    """

    scene: int

    title: str

    duration: int

    lines: list[ScriptLine] = Field(default_factory=list)


class ScriptData(BaseModel):
    """
    Complete documentary script.
    """

    scenes: list[ScriptScene] = Field(default_factory=list)


class ScriptSceneResponse(BaseModel):
    """
    Returned by the LLM when generating ONE script scene.
    """

    scene: ScriptScene