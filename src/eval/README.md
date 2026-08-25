# Evaluation results

I ran two experiments. Both experiments used the same test cases which are defined in the `test_cases.py` file.

## Results:
1. The first experiment measured the latency of the system modules. 
Measurements were performed on a `MacBook Pro M2 Max`.  

Raw results:

`./run.sh --local --performance-test`

```
======================================================================
END-TO-END PERFORMANCE
======================================================================
Requests:       50
Successful:     50
Errors:         0
Mean latency:   12.95020s
P50 latency:    12.19242s
P95 latency:    19.66342s
P99 latency:    23.06385s
Min latency:    6.29471s
Max latency:    27.28779s
Throughput:     0.07722 req/s
Error rate:     0.00000%

======================================================================
MODULE PERFORMANCE
======================================================================

summarize
  calls:   50
  mean:    4.27321s
  p50:     4.81192s
  p95:     6.71449s
  max:     9.47994s

create_plan
  calls:   50
  mean:    4.10360s
  p50:     3.98356s
  p95:     6.47391s
  max:     6.81160s

agent
  calls:   115
  mean:    3.25654s
  p50:     3.19774s
  p95:     4.87116s
  max:     6.81172s

review_completed_work
  calls:   62
  mean:    2.73069s
  p50:     2.98938s
  p95:     4.42887s
  max:     6.14724s

user_query_refinement
  calls:   50
  mean:    1.14869s
  p50:     1.17212s
  p95:     1.24041s
  max:     1.24726s

retrieve
  calls:   60
  mean:    0.02150s
  p50:     0.02400s
  p95:     0.04367s
  max:     0.04871s

select_next_task
  calls:   161
  mean:    0.00003s
  p50:     0.00002s
  p95:     0.00014s
  max:     0.00016s

tool
  calls:   36
  mean:    0.00001s
  p50:     0.00000s
  p95:     0.00001s
  max:     0.00001s

rerank
  calls:   60
  mean:    0.00000s
  p50:     0.00000s
  p95:     0.00000s
  max:     0.00001s

get_unfinished_tasks
  calls:   273
  mean:    0.00000s
  p50:     0.00000s
  p95:     0.00000s
  max:     0.00001s

route_query
  calls:   50
  mean:    0.00000s
  p50:     0.00000s
  p95:     0.00000s
  max:     0.00001s

route_agent
  calls:   115
  mean:    0.00000s
  p50:     0.00000s
  p95:     0.00000s
  max:     0.00000s

route_task
  calls:   161
  mean:    0.00000s
  p50:     0.00000s
  p95:     0.00000s
  max:     0.00000s
```

The main bottleneck is where we call the SLM modules. The system could be improved in several ways:
- Prompt optimization: Smaller prompts reduce the SLM inference time.
- Cache frequent answers for frequent queries. 
- Introduce prompt-caching: Reuse static parts of the prompt when supported by the inference framework, reducing repeated computation.
- Investigate other smaller models.
- Use more powerful hardware or GPU acceleration.


2. The second test evaluated the `agent` node, whether its decided `plan` equals our pre-defined plans in the test cases file. Raw results:

`./run.sh --local --eval`

```
build_graph took 0.0045 seconds
user_query_refinement took 1.0351 seconds
get_unfinished_tasks took 0.0000 seconds
create_plan took 2.5479 seconds
agent took 2.5479 seconds

======================================================================
Query:    Tell me about NVIDIA
Expected: ['RAG']
Actual:   ['RAG']
Result:   PASS
user_query_refinement took 0.9992 seconds
get_unfinished_tasks took 0.0000 seconds
create_plan took 2.7702 seconds
agent took 2.7703 seconds

======================================================================
Query:    What is NVIDIA's current stock price?
Expected: ['TOOL']
Actual:   ['TOOL']
Result:   PASS
user_query_refinement took 1.0862 seconds
get_unfinished_tasks took 0.0000 seconds
create_plan took 3.2853 seconds
agent took 3.2853 seconds

======================================================================
Query:    What is Apple's latest revenue?
Expected: ['TOOL']
Actual:   ['TOOL']
Result:   PASS
user_query_refinement took 1.0942 seconds
get_unfinished_tasks took 0.0000 seconds
create_plan took 3.8670 seconds
agent took 3.8671 seconds

======================================================================
Query:    Compare NVIDIA and Apple companies
Expected: ['RAG', 'RAG']
Actual:   ['RAG', 'RAG']
Result:   PASS
user_query_refinement took 1.0403 seconds
get_unfinished_tasks took 0.0000 seconds
create_plan took 3.8637 seconds
agent took 3.8638 seconds

======================================================================
Query:    Compare Amazon and NVIDIA
Expected: ['RAG', 'RAG']
Actual:   ['RAG', 'RAG']
Result:   PASS
user_query_refinement took 1.2673 seconds
get_unfinished_tasks took 0.0000 seconds
create_plan took 4.1208 seconds
agent took 4.1209 seconds

======================================================================
Query:    Tell me about Microsoft's business and its current stock price
Expected: ['RAG', 'TOOL']
Actual:   ['RAG', 'TOOL']
Result:   PASS
user_query_refinement took 1.2330 seconds
get_unfinished_tasks took 0.0000 seconds
create_plan took 6.2982 seconds
agent took 6.2983 seconds

======================================================================
Query:    Compare Apple and NVIDIA and give me their current stock prices
Expected: ['RAG', 'RAG', 'TOOL', 'TOOL']
Actual:   ['RAG', 'RAG', 'TOOL', 'TOOL']
Result:   PASS
user_query_refinement took 1.2204 seconds
get_unfinished_tasks took 0.0000 seconds
create_plan took 4.2510 seconds
agent took 4.2511 seconds

======================================================================
Query:    What are Amazon's main business areas and latest EPS?
Expected: ['RAG', 'TOOL']
Actual:   ['RAG', 'TOOL']
Result:   PASS
user_query_refinement took 1.1638 seconds
get_unfinished_tasks took 0.0000 seconds
create_plan took 3.0925 seconds
agent took 3.0926 seconds

======================================================================
Query:    Tell me about Meta and its latest EPS
Expected: ['RAG', 'TOOL']
Actual:   ['RAG']
Result:   FAIL

Generated plan:
  1: RAG - Retrieve information about Meta, including its business model and products/services.
user_query_refinement took 1.1999 seconds
get_unfinished_tasks took 0.0000 seconds
create_plan took 3.9314 seconds
agent took 3.9314 seconds

======================================================================
Query:    Compare Microsoft and Google and give me their stock prices
Expected: ['RAG', 'RAG', 'TOOL', 'TOOL']
Actual:   ['RAG', 'RAG']
Result:   FAIL

Generated plan:
  1: RAG - Retrieve qualitative company information about Microsoft
  2: RAG - Retrieve qualitative company information about Google

======================================================================
PLANNER EVALUATION
Correct:  8/10
Accuracy: 80.0%
```

The planner-action module achieved 80% accuracy on the 10 test cases. However we shall not forget that the number of test cases is low and I created relatively simple problems. I've also heavily optimized the prompt to cover these cases. Therefore, this result should not be interpreted as general planner accuracy, and the system may fail on more complex or previously unseen problems.
Additionally, the two failed test cases shows similar patterns: The planner module handles well the RAG case, meanwhile sometimes tool usage forgotten about. 