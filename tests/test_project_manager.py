from orchestrator.project_manager import ProjectManager

manager = ProjectManager()

project = manager.create_project(
    title="History of Rome",
    topic="The Rise and Fall of the Roman Empire",
    audience="General Public",
    duration_seconds=600,
)

print(f"Project ID : {project.project_id}")
print(f"Title      : {project.metadata.title}")