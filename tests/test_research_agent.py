from agents.executive_producer import ExecutiveProducer
from agents.researcher import ResearchAgent


producer = ExecutiveProducer()

researcher = ResearchAgent()


state = producer.run(
    "Create a ten minute documentary about sharks."
)

state = researcher.run(state)


print("=" * 80)
print("PROJECT STATE")
print("=" * 80)

print(
    state.model_dump_json(
        indent=4,
    )
)