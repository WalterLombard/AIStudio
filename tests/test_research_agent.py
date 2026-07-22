from pprint import pprint

from agents.executive_producer.agent import ExecutiveProducerAgent
from agents.researcher.agent import ResearchAgent
from shared.models import ProjectState

state = ProjectState()
state.project.topic = "Sharks"

producer = ExecutiveProducerAgent()
state = producer.run(state)

researcher = ResearchAgent()
state = researcher.run(state)

print()
print("=" * 80)
print("RESEARCH DATA")
print("=" * 80)

if getattr(state, "research", None):
    pprint(
        state.research.model_dump(),
        sort_dicts=False,
    )
else:
    print("Research stage produced no output or state.research is None.")