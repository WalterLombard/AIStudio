from agents.base_agent import BaseAgent
from shared.models import ProjectState


class TestAgent(BaseAgent):

    def __init__(self):

        super().__init__("TestAgent")

    def run(self, project: ProjectState) -> ProjectState:

        project.status = "processed"

        return project


project = ProjectState(project_id="TEST001")

agent = TestAgent()

project = agent.execute(project)

print(project.status)