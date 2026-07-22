import json
from shared.models import ProjectState
from agents.executive_producer.agent import ExecutiveProducerAgent
from agents.researcher.agent import ResearchAgent
from agents.script_writer.agent import ScriptWriterAgent

state = ProjectState()
state.project.topic = "Create a ten minute documentary about sharks."

producer = ExecutiveProducerAgent()
researcher = ResearchAgent()
writer = ScriptWriterAgent()

print("-> Consulting Executive Producer...")
state = producer.run(state)
print("Executive Producer Complete.\n")

print("-> Consulting Research Agent...")
state = researcher.run(state)
print("Research Complete.\n")

print("-> Consulting Script Writer...")
state = writer.run(state)
print("Script Complete.\n")

print("=" * 80)
print("FINAL SCRIPT")
print("=" * 80)

if getattr(state, "script", None):
    print(
        json.dumps(
            state.script.model_dump() if hasattr(state.script, "model_dump") else state.script,
            indent=4,
        )
    )
else:
    print("Script stage produced no output.")