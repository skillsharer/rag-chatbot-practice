import statistics
import time
from collections import defaultdict
from src.backend.graph.graph import BackendStateMachine
from src.backend.utils.latency import get_timings, reset_timings
from src.eval.test_cases import TEST_CASES
from src.config import NUM_REQUESTS, WARMUP_REQUESTS


def percentile(values, p):
    values = sorted(values)
    index = int((p / 100) * (len(values) - 1))
    return values[index]


def run_query(backend, query, request_id):
    reset_timings()
    start = time.perf_counter()
    backend.graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": query,
                }
            ]
        },
        config={
            "configurable": {
                "thread_id": f"performance-{request_id}",
            }
        },
    )
    total_latency = time.perf_counter() - start
    module_timings = get_timings()

    return total_latency, module_timings

def print_system_results(latencies, errors, total_test_time):
    print(f"\n{'=' * 70}")
    print("END-TO-END PERFORMANCE")
    print(f"{'=' * 70}")
    print(f"Requests:       {NUM_REQUESTS}")
    print(f"Successful:     {len(latencies)}")
    print(f"Errors:         {errors}")

    if not latencies:
        return

    print(
        f"Mean latency:   "
        f"{statistics.mean(latencies):.5f}s"
    )
    print(
        f"P50 latency:    "
        f"{statistics.median(latencies):.5f}s"
    )
    print(
        f"P95 latency:    "
        f"{percentile(latencies, 95):.5f}s"
    )
    print(
        f"P99 latency:    "
        f"{percentile(latencies, 99):.5f}s"
    )
    print(
        f"Min latency:    "
        f"{min(latencies):.5f}s"
    )
    print(
        f"Max latency:    "
        f"{max(latencies):.5f}s"
    )
    print(
        f"Throughput:     "
        f"{len(latencies) / total_test_time:.5f} req/s"
    )
    print(
        f"Error rate:     "
        f"{errors / NUM_REQUESTS:.5%}"
    )


def print_module_results(module_results):
    print(f"\n{'=' * 70}")
    print("MODULE PERFORMANCE")
    print(f"{'=' * 70}")
    for module, latencies in sorted(module_results.items(), key=lambda item: statistics.mean(item[1]), reverse=True):
        print(f"\n{module}")
        print(f"  calls:   {len(latencies)}")
        print(
            f"  mean:    "
            f"{statistics.mean(latencies):.5f}s"
        )
        print(
            f"  p50:     "
            f"{statistics.median(latencies):.5f}s"
        )
        print(
            f"  p95:     "
            f"{percentile(latencies, 95):.5f}s"
        )
        print(
            f"  max:     "
            f"{max(latencies):.5f}s"
        )

def measure():
    backend = BackendStateMachine()
    queries = [test["query"] for test in TEST_CASES]

    print(f"Running {WARMUP_REQUESTS} warmup requests...")
    for i in range(WARMUP_REQUESTS):
        run_query(
            backend=backend,
            query=queries[i % len(queries)],
            request_id=f"warmup-{i}",
        )

    total_latencies = []
    module_results = defaultdict(list)
    errors = 0
    print(f"\nRunning {NUM_REQUESTS} measured requests...\n")
    test_start = time.perf_counter()

    for i in range(NUM_REQUESTS):
        query = queries[i % len(queries)]

        try:
            total_latency, timings = run_query(backend=backend, query=query, request_id=i)
            total_latencies.append(total_latency)

            for timing in timings:
                module_results[timing["module"]].append(timing["latency"])

            print(f"{i + 1:03}/{NUM_REQUESTS} ", f"{total_latency:.3f}s - {query}")

        except Exception as e:
            errors += 1

            print(f"{i + 1:03}/{NUM_REQUESTS} ", f"ERROR - {query}: {e}")

    total_test_time = (time.perf_counter() - test_start)

    print_system_results(total_latencies, errors, total_test_time)
    print_module_results(module_results)


if __name__ == "__main__":
    measure()