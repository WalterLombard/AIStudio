from pprint import pprint

from agents.executive_producer.agent import ExecutiveProducerAgent
from agents.outline.agent import OutlineAgent
from agents.researcher.agent import ResearchAgent
from shared.models import ProjectState

state = ProjectState()
state.project.topic = "Sharks"

producer = ExecutiveProducerAgent()
state = producer.run(state)

researcher = ResearchAgent()
state = researcher.run(state)

outliner = OutlineAgent()
state = outliner.run(state)

print()
print("=" * 80)
print("OUTLINE")
print("=" * 80)

if getattr(state, "outline", None):
    pprint(
        state.outline.model_dump(),
        sort_dicts=False,
    )
else:
    print("Outline stage produced no output.")