import json

from agents.executive_producer import ExecutiveProducer
from agents.researcher import ResearchAgent
from agents.outline import OutlineAgent


producer = ExecutiveProducer()
researcher = ResearchAgent()
outliner = OutlineAgent()


print("Executive Producer...\n")

brief = producer.run(
    "Create a ten minute documentary about sharks."
)

print("Research...\n")

research = researcher.run(
    brief
)

print("Outline...\n")

outline = outliner.run(
    brief,
    research
)

print("\n" + "=" * 80)
print("DOCUMENTARY OUTLINE")
print("=" * 80)

print(
    json.dumps(
        outline,
        indent=4
    )
)