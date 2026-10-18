import uuid

from app.graph import compiled_graph


def test():
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    print("1. Invoking graph...")

    compiled_graph.invoke(
        {
            "raw_inbound_text": "Hi, I am Sarah from TechNova. We need enterprise pricing.",
            "trace": [],
        },
        config=config,
    )

    print("2. Graph invoked successfully. Checking state...")
    state = compiled_graph.get_state(config)

    print(f"3. State 'next' (pause points): {state.next}")

    if state.next:
        print("4. Graph paused! Extracting payload...")
        payload = state.tasks[0].interrupts[0].value
        print(f"5. Payload: {payload}")
    else:
        print("4. Graph finished without pausing.")


if __name__ == "__main__":
    test()
