from agents.executive_producer.agent import ExecutiveProducer


agent = ExecutiveProducer()

response = agent.run(

    "Create a ten minute documentary about sharks."

)

print(response)