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
Requests:       10
Successful:     10
Errors:         0
Mean latency:   11.23607s
P50 latency:    11.69968s
P95 latency:    14.51543s
P99 latency:    14.51543s
Min latency:    6.58981s
Max latency:    16.27222s
Throughput:     0.08900 req/s
Error rate:     0.00000%

======================================================================
MODULE PERFORMANCE
======================================================================

create_plan
  calls:   10
  mean:    4.04715s
  p50:     3.81035s
  p95:     4.68781s
  max:     6.67702s

summarize
  calls:   10
  mean:    4.01930s
  p50:     4.54772s
  p95:     6.33764s
  max:     6.42142s

agent
  calls:   20
  mean:    3.02338s
  p50:     3.09372s
  p95:     4.68792s
  max:     6.67738s

review_completed_work
  calls:   10
  mean:    1.99928s
  p50:     1.96627s
  p95:     2.95681s
  max:     3.15247s

user_query_refinement
  calls:   10
  mean:    1.13489s
  p50:     1.12914s
  p95:     1.25145s
  max:     1.26831s

retrieve
  calls:   10
  mean:    0.02353s
  p50:     0.02412s
  p95:     0.02908s
  max:     0.04247s

select_next_task
  calls:   27
  mean:    0.00004s
  p50:     0.00002s
  p95:     0.00013s
  max:     0.00015s

tool
  calls:   7
  mean:    0.00001s
  p50:     0.00001s
  p95:     0.00001s
  max:     0.00001s

rerank
  calls:   10
  mean:    0.00000s
  p50:     0.00000s
  p95:     0.00000s
  max:     0.00000s

get_unfinished_tasks
  calls:   47
  mean:    0.00000s
  p50:     0.00000s
  p95:     0.00000s
  max:     0.00001s

route_agent
  calls:   20
  mean:    0.00000s
  p50:     0.00000s
  p95:     0.00000s
  max:     0.00000s

route_query
  calls:   10
  mean:    0.00000s
  p50:     0.00000s
  p95:     0.00000s
  max:     0.00000s

route_task
  calls:   27
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
user_query_refinement took 1.0032 seconds
get_unfinished_tasks took 0.0000 seconds
create_plan took 2.5407 seconds
agent took 2.5408 seconds

======================================================================
Query:    Tell me about NVIDIA
Expected: ['RAG']
Actual:   ['RAG']
Result:   PASS
user_query_refinement took 1.0126 seconds
get_unfinished_tasks took 0.0000 seconds
create_plan took 2.7981 seconds
agent took 2.7982 seconds

======================================================================
Query:    What is NVIDIA's current stock price?
Expected: ['TOOL']
Actual:   ['TOOL']
Result:   PASS
user_query_refinement took 1.1513 seconds
get_unfinished_tasks took 0.0000 seconds
create_plan took 3.2714 seconds
agent took 3.2715 seconds

======================================================================
Query:    What is Apple's latest revenue?
Expected: ['TOOL']
Actual:   ['TOOL']
Result:   PASS
user_query_refinement took 1.1095 seconds
get_unfinished_tasks took 0.0000 seconds
create_plan took 3.8558 seconds
agent took 3.8559 seconds

======================================================================
Query:    Compare NVIDIA and Apple companies
Expected: ['RAG', 'RAG']
Actual:   ['RAG', 'RAG']
Result:   PASS
user_query_refinement took 1.0500 seconds
get_unfinished_tasks took 0.0000 seconds
create_plan took 3.8909 seconds
agent took 3.8910 seconds

======================================================================
Query:    Compare Amazon and NVIDIA
Expected: ['RAG', 'RAG']
Actual:   ['RAG', 'RAG']
Result:   PASS
user_query_refinement took 1.1917 seconds
get_unfinished_tasks took 0.0000 seconds
create_plan took 4.2397 seconds
agent took 4.2398 seconds

======================================================================
Query:    Tell me about Microsoft's business and its current stock price
Expected: ['RAG', 'TOOL']
Actual:   ['RAG', 'TOOL']
Result:   PASS
user_query_refinement took 1.1940 seconds
get_unfinished_tasks took 0.0000 seconds
create_plan took 6.4191 seconds
agent took 6.4192 seconds

======================================================================
Query:    Compare Apple and NVIDIA and give me their current stock prices
Expected: ['RAG', 'RAG', 'TOOL', 'TOOL']
Actual:   ['RAG', 'RAG', 'TOOL', 'TOOL']
Result:   PASS
user_query_refinement took 1.1889 seconds
get_unfinished_tasks took 0.0000 seconds
create_plan took 4.3842 seconds
agent took 4.3843 seconds

======================================================================
Query:    What are Amazon's main business areas and latest EPS?
Expected: ['RAG', 'TOOL']
Actual:   ['RAG', 'TOOL']
Result:   PASS

======================================================================
PLANNER EVALUATION
Correct:  8/8
Accuracy: 100.0%
```

The planner-action module achieved 100% accuracy on the 8 test cases. However we shall not forget that the number of test cases is low and I created relatively simple problems. I've also heavily optimized the prompt to cover these cases. Therefore, this result should not be interpreted as general planner accuracy, and the system may fail on more complex or previously unseen problems.