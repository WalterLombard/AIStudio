"""
AIStudio Storyboard Models

Defines the cinematic storyboard for the documentary.

The storyboard translates the completed script into a visual sequence
of scenes and shots that will later be expanded into detailed shot
plans for image generation, animation and final video production.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class StoryboardShot(BaseModel):
    """
    A single cinematic shot within a storyboard scene.
    """

    shot_number: int

    shot_type: str = ""

    subject: str = ""

    visual_goal: str = ""

    location: str = ""

    time_of_day: str = ""

    camera_move: str = ""

    lens: str = ""

    framing: str = ""

    lighting: str = ""

    mood: str = ""

    duration: float = 0.0

    prompt: str = ""

    narration: str = ""

    sound_effects: list[str] = Field(default_factory=list)

    transition_to_next: str = ""

    continuity_notes: str = ""

    notes: str = ""


class StoryboardScene(BaseModel):
    """
    A storyboard representation of one documentary scene.
    """

    scene_number: int

    title: str = ""

    scene_goal: str = ""

    estimated_duration: float = 0.0

    transition_in: str = ""

    transition_out: str = ""

    shots: list[StoryboardShot] = Field(
        default_factory=list,
    )


class StoryboardData(BaseModel):
    """
    Complete storyboard for the documentary.
    """

    title: str = ""

    scene_count: int = 0

    total_duration: float = 0.0

    scenes: list[StoryboardScene] = Field(
        default_factory=list,
    )


class StoryboardSceneResponse(BaseModel):
    """
    Returned by the LLM when generating ONE storyboard scene.
    """

    scene: StoryboardScene