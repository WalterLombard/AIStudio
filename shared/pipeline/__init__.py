"""
AIStudio Pipeline Package

Provides the public interface for executing the complete
AIStudio production pipeline.

Author : AIStudio
"""

from .runner import PipelineRunner

__all__ = [
    "PipelineRunner",
]