from shared.project_models import ProjectState


state = ProjectState()

print()

print("=" * 80)
print("EMPTY PROJECT")
print("=" * 80)

print(state.model_dump_json(indent=4))