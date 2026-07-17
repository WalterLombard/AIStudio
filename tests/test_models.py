from shared.models import ProjectState

print("ProjectState loaded from:")
print(ProjectState.__module__)
print()

project = ProjectState(project_id="TEST001")

print(project.model_dump_json(indent=2))