from agents.executive_producer.agent import ExecutiveProducer
from agents.researcher.agent import ResearchAgent
from agents.outline.agent import OutlineAgent
from agents.script_writer.agent import ScriptWriterAgent
from agents.storyboard.agent import StoryboardAgent

from shared.models import ProjectState


print("=" * 80)
print("AISTUDIO STORYBOARD AGENT TEST")
print("=" * 80)

state = ProjectState()

producer = ExecutiveProducer()
researcher = ResearchAgent()
outliner = OutlineAgent()
writer = ScriptWriterAgent()
storyboard = StoryboardAgent()

state = producer.run(
    "Create a documentary about sharks.",
    state,
)

state = researcher.run(state)

state = outliner.run(state)

state = writer.run(state)

state = storyboard.run(state)

print()
print("=" * 80)
print("STORYBOARD GENERATED")
print("=" * 80)

print(state.storyboard.model_dump_json(indent=4))