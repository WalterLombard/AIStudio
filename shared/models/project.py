from pydantic import BaseModel
from datetime import datetime


class ProjectInfo(BaseModel):
    project_name: str = ""
    topic: str = ""
    created: datetime = datetime.now()
    modified: datetime = datetime.now()