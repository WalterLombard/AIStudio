from agents.executive_producer.agent import ExecutiveProducer


def test_executive_producer():
    agent = ExecutiveProducer()

    state = agent.run(
        "Create a ten minute documentary about sharks."
    )

    print("\n" + "=" * 80)
    print("PROJECT STATE")
    print("=" * 80)
    print(state.model_dump_json(indent=4))

    assert state is not None
    assert state.status != "failed"


if __name__ == "__main__":
    test_executive_producer()