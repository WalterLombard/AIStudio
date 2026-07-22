from shared.models import ProjectState
from agents.base_agent import BaseAgent


class TestAgent(BaseAgent):

    def __init__(self):
        super().__init__("TestAgent")

    def run(self, project: ProjectState) -> ProjectState:
        project.status = "processed"
        return project


def test_agent_execution():
    project = ProjectState(project_id="TEST001")
    agent = TestAgent()

    # Fixed: calling run() instead of execute()
    project = agent.run(project)

    print(f"Project Status: {project.status}")
    assert project.status == "processed"


if __name__ == "__main__":
    test_agent_execution()