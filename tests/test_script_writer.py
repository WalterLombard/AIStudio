import json

from agents.executive_producer import ExecutiveProducer
from agents.researcher import ResearchAgent
from agents.script_writer import ScriptWriter


producer = ExecutiveProducer()
researcher = ResearchAgent()
writer = ScriptWriter()


print("-> Consulting Executive Producer...")

brief = producer.run(
    "Create a ten minute documentary about sharks."
)

print("Executive Producer Complete.\n")


print("-> Consulting Research Agent...")

research = researcher.run(
    brief
)

print("Research Complete.\n")


print("-> Consulting Script Writer...")

script = writer.run(
    brief,
    research
)

print("Script Complete.\n")


print("=" * 80)
print("FINAL SCRIPT")
print("=" * 80)

print(
    json.dumps(
        script,
        indent=4
    )
)