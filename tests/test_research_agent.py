import json

from agents.executive_producer import ExecutiveProducer
from agents.researcher import ResearchAgent


producer = ExecutiveProducer()

researcher = ResearchAgent()

brief = producer.run(

    "Create a ten minute documentary about sharks."

)

print("=" * 60)
print("PRODUCTION BRIEF")
print("=" * 60)
print(brief)

research = researcher.run(brief)

print("=" * 60)
print("RESEARCH")
print("=" * 60)
print(research)