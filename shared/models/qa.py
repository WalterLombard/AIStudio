from pydantic import BaseModel, Field


class QAIssue(BaseModel):
    severity: str = ""

    message: str = ""

    stage: str = ""


class QAReport(BaseModel):
    passed: bool = False

    issues: list[QAIssue] = Field(default_factory=list)