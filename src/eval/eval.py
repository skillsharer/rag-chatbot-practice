from src.backend.graph.graph import BackendStateMachine
from src.eval.test_cases import TEST_CASES


def evaluate_plan(backend, query):
    refinement_state = {
        "messages": [
            {
                "role": "user",
                "content": query,
            }
        ]
    }

    refined = backend.user_query_refinement(refinement_state)

    agent_state = {
        **refinement_state,
        **refined,
    }

    planned = backend.agent(agent_state)

    return planned.get("plan", [])


def extract_task_types(plan):
    return [task["type"] for task in plan]


def main():
    backend = BackendStateMachine()

    correct = 0

    for test in TEST_CASES:
        plan = evaluate_plan(
            backend=backend,
            query=test["query"],
        )

        actual_types = extract_task_types(plan)
        expected_types = test["expected_types"]

        passed = sorted(actual_types) == sorted(expected_types)

        if passed:
            correct += 1

        print(f"\n{'=' * 70}")
        print(f"Query:    {test['query']}")
        print(f"Expected: {expected_types}")
        print(f"Actual:   {actual_types}")
        print(f"Result:   {'PASS' if passed else 'FAIL'}")

        if not passed:
            print("\nGenerated plan:")

            for task in plan:
                print(
                    f"  {task['task_id']}: "
                    f"{task['type']} - "
                    f"{task['task']}"
                )

    total = len(TEST_CASES)
    accuracy = correct / total

    print(f"\n{'=' * 70}")
    print("PLANNER EVALUATION")
    print(f"Correct:  {correct}/{total}")
    print(f"Accuracy: {accuracy:.1%}")


if __name__ == "__main__":
    main()