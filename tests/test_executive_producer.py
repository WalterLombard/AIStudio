from agents.executive_producer.agent import ExecutiveProducer


agent = ExecutiveProducer()

state = agent.run(

    "Create a ten minute documentary about sharks."

)

print("\n" + "=" * 80)
print("PROJECT STATE")
print("=" * 80)

print(state.model_dump_json(indent=4))