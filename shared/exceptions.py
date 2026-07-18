"""
AIStudio Custom Exceptions

All custom exceptions used throughout AIStudio should inherit from
AIStudioError.

Author : AIStudio
"""

from __future__ import annotations


class AIStudioError(Exception):
    """
    Base exception for AIStudio.
    """
    pass


# ==========================================================
# Configuration
# ==========================================================

class ConfigurationError(AIStudioError):
    """
    Raised when configuration is invalid or missing.
    """
    pass


# ==========================================================
# LLM
# ==========================================================

class LLMError(AIStudioError):
    """
    Raised when an LLM request fails.
    """
    pass


class LLMResponseError(LLMError):
    """
    Raised when the LLM returns invalid JSON or
    an unexpected response.
    """
    pass


# ==========================================================
# Project
# ==========================================================

class ProjectError(AIStudioError):
    """
    Raised when the project state is invalid.
    """
    pass


class MissingProjectDataError(ProjectError):
    """
    Raised when required project data is missing.
    """
    pass


# ==========================================================
# Agent
# ==========================================================

class AgentError(AIStudioError):
    """
    Base exception for all AIStudio agents.
    """
    pass


class AgentExecutionError(AgentError):
    """
    Raised when an agent fails during execution.
    """
    pass


# ==========================================================
# Parsing
# ==========================================================

class ParserError(AIStudioError):
    """
    Raised when parsing fails.
    """
    pass


# ==========================================================
# Assets
# ==========================================================

class AssetError(AIStudioError):
    """
    Raised when an asset cannot be created or loaded.
    """
    pass


# ==========================================================
# Video
# ==========================================================

class VideoCompilationError(AIStudioError):
    """
    Raised when video compilation fails.
    """
    pass


# ==========================================================
# Audio
# ==========================================================

class AudioGenerationError(AIStudioError):
    """
    Raised when audio generation fails.
    """
    pass