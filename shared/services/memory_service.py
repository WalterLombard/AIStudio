"""
AIStudio Project Memory Service

Provides centralized, structured context management and retrieval 
for downstream agents without bloating LLM prompt payloads.

Author : AIStudio
"""

from __future__ import annotations

from typing import Any


class ProjectMemory:
    """
    Manages structured context, scene summaries, and targeted lookups
    across the AIStudio pipeline.
    """

    def __init__(self) -> None:
        self.scene_summaries: dict[int, dict[str, Any]] = {}
        self.key_entities: dict[str, list[str]] = {
            "terms": [],
            "locations": [],
            "people": [],
        }
        self.global_metadata: dict[str, Any] = {}

    def store_scene(self, scene_number: int, scene_data: dict[str, Any]) -> None:
        """
        Store a compressed, structured summary of a completed scene.
        """
        self.scene_summaries[scene_number] = {
            "scene_number": scene_number,
            "title": scene_data.get("title"),
            "goal": scene_data.get("goal"),
            "key_points": scene_data.get("key_points", []),
            "emotional_tone": scene_data.get("emotional_tone"),
            "visual_focus": scene_data.get("visual_focus"),
        }

    def get_preceding_scene_context(self, current_scene_number: int) -> dict[str, Any] | None:
        """
        Retrieve only the immediately preceding scene context for continuity.
        """
        prev_num = current_scene_number - 1
        return self.scene_summaries.get(prev_num)

    def get_compact_outline_summary(self) -> list[dict[str, Any]]:
        """
        Return a high-level list of all scene titles and goals for global context.
        """
        return [
            {
                "scene_number": num,
                "title": data["title"],
                "goal": data["goal"]
            }
            for num, data in sorted(self.scene_summaries.items())
        ]

    def register_entities(self, category: str, items: list[str]) -> None:
        """
        Register key terms, locations, or people for cross-reference.
        """
        if category in self.key_entities:
            for item in items:
                if item not in self.key_entities[category]:
                    self.key_entities[category].append(item)

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize memory state for storage in ProjectState.
        """
        return {
            "scene_summaries": self.scene_summaries,
            "key_entities": self.key_entities,
            "global_metadata": self.global_metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProjectMemory:
        """
        Reconstruct memory state from serialized data.
        """
        instance = cls()
        instance.scene_summaries = data.get("scene_summaries", {})
        instance.key_entities = data.get("key_entities", {"terms": [], "locations": [], "people": []})
        instance.global_metadata = data.get("global_metadata", {})
        return instance