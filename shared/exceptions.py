class AIStudioError(Exception):
    pass


class ConfigurationError(AIStudioError):
    pass


class ProjectError(AIStudioError):
    pass


class AgentError(AIStudioError):
    pass


class EngineError(AIStudioError):
    pass