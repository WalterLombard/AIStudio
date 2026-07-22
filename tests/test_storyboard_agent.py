from shared.models import ProjectState
from agents.executive_producer.agent import ExecutiveProducerAgent
from agents.researcher.agent import ResearchAgent
from agents.outline.agent import OutlineAgent
from agents.script_writer.agent import ScriptWriterAgent
from agents.storyboard.agent import StoryboardAgent

print("=" * 80)
print("AISTUDIO STORYBOARD AGENT TEST")
print("=" * 80)

state = ProjectState()
state.project.topic = "Create a documentary about sharks."

producer = ExecutiveProducerAgent()
researcher = ResearchAgent()
outliner = OutlineAgent()
writer = ScriptWriterAgent()
storyboard = StoryboardAgent()

state = producer.run(state)
state = researcher.run(state)
state = outliner.run(state)
state = writer.run(state)
state = storyboard.run(state)

print()
print("=" * 80)
print("STORYBOARD GENERATED")
print("=" * 80)

if getattr(state, "storyboard", None):
    print(state.storyboard.model_dump_json(indent=4))
else:
    print("Storyboard stage produced no output.")