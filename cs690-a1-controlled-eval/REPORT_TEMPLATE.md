
---

# CS 690 Assignment 1 Report: Replicating a Controlled Evaluation

**Name:** Kundan Singh  
**Repository Link:** `https://github.com/KKS071/cs690-assignment1`  
**Short SHA of results commit:** 9e157c5  

---

## Part 1. Verification evidence

Command:

```text
python -m harness.verify
```

OK: loaded 20 frozen tasks  
OK: dataset sha256 5d84176547cb679f4145676d1f4dfd5061bf3b9600904911da8e5700e82eee3b  
OK: generated Python executed in Docker sandbox  
OK: candidate network probe was blocked  
OK: model/configuration metadata written to results/verification.json  

---

## Part 2. Tests and code questions

Final summary line of `pytest -q`:

```
....................    [100%]
20 passed in 1.15s
```

### Q1. The path of one attempt

Each attempt begins with a problem entry in `tasks/cs690_eval20.json`, which defines the function name, prompt, and tests. The harness loads these tasks through `harness/tasks.py`, which also verifies the dataset fingerprint to ensure the file has not changed. For each task, `harness/provider.py` constructs the API request using the settings from `conditions.json` and sends it to the model. The model’s full reply is captured, and `harness/grader.py` extracts the Python code block from the response. That extracted code is executed inside the Docker sandbox through `harness/sandbox.py` and `harness/docker_entry.py`, which run the tests and return a pass/fail verdict. Finally, `harness/runner.py` writes a row into `results/experiment/raw_results.jsonl` containing the settings, model version, token counts, and verdict. The code runs in Docker to ensure safety, isolation, no network access, and consistent resource limits.

### Q2. What is sent and what comes back

The settings sent with each request come from `conditions.json` and `harness/provider.py`. They include the requested model name, temperature (1.0), max output tokens, stop sequences, and the number of samples per task (3). Temperature controls randomness; max tokens limit the length of the model’s answer; stop sequences define where generation should end. The harness also sends the exact prompt for the task, including the function signature and instructions.

From each reply, the harness keeps the returned model version string, the raw text of the answer, the extracted Python code, input and output token counts, the stop reason, and the timestamp. It also records whether the code passed the tests. The requested model name alone is insufficient because OpenAI may return different version strings over time. The version string is essential for reproducibility and for identifying exactly which model produced the answer.

### Q3. Same prompt, different answers

Both conditions use temperature 1.0, which introduces randomness into generation. Because no seed is set, each attempt samples independently from the model’s distribution, so the three attempts for a single problem can differ. This variation is intentional because the experiment measures pass@k, which depends on multiple independent tries. The harness records everything needed for reproducibility: the prompts in `prompts/a1-controlled-eval-fall2026/`, the configuration in `conditions.json`, the dataset fingerprint in `results/experiment/manifest.json`, and every attempt in `results/experiment/raw_results.jsonl`. Each row includes the returned model version, settings, token counts, and verdict. With these files, another person can rerun the same experiment and verify the results, even though individual attempts may differ due to sampling.

### Q4. pass@k by hand

For one task with n = 3 attempts and c = 1 correct:

pass@1 = c / n = 1 / 3 ≈ 0.3333

For pass@2, using the lecture formula:

pass@2 = 1 − [(n − c choose 2) / (n choose 2)]

Here, n − c = 2, so:

(n − c choose 2) = (2 choose 2) = 1  
(n choose 2) = (3 choose 2) = 3  

So:

pass@2 = 1 − (1 / 3) = 2 / 3 ≈ 0.6667

Confirming with pass_at_k(3, 3, 1) gives the same values.

The shortcut formula:

1 − (1 − c/n)^k = 1 − (2/3)^2 = 1 − 4/9 = 5/9 ≈ 0.5556

This differs because the shortcut treats attempts as independent draws with replacement. The correct pass@k formula uses combinations without replacement, matching how coding benchmarks define pass@k. That is why the shortcut is incorrect here.


### Q5. Why whole problems are redrawn

`bootstrap_task_ci` computes the 95% confidence interval by repeatedly resampling tasks, not individual attempts. Each bootstrap sample draws 20 tasks with replacement and recomputes pass@1 for that synthetic dataset. This preserves the structure of the benchmark: each task contributes one pass@1 value based on its three attempts. If attempts were resampled individually, it would artificially inflate the amount of data and underestimate uncertainty.

The rule is enforced by the test `test_bootstrap_task_ci_resamples_tasks` in `tests/test_metrics.py`. This test checks that the bootstrap function redraws whole tasks and never mixes attempts across tasks. It verifies that the resampled indices correspond to task-level units. This ensures the confidence interval reflects variability across tasks, which is the correct interpretation for coding benchmarks.

---

## Part 3. Replication

Evidence is contained in the committed `results/experiment/` and `prompts/` folders.  
Dollars spent: **$0.07**

---

## Part 4. Results

| Field | Condition A | Condition B |
| --- | --- | --- |
| Condition ID | A | B |
| Requested Model | gpt‑5.6‑luna | gpt‑5.6‑terra |
| Returned Model Version | gpt‑5.6‑luna | gpt‑5.6‑terra |
| Attempts per Task | 3 | 3 |
| Total Attempts | 60 | 60 |
| pass@1 | 0.9666666667 | 1.0 |
| 95% CI (pass@1) | [0.90, 1.00] | [1.00, 1.00] |
| pass@2 | 0.9833333333 | 1.0 |
| Input Tokens | 7146 | 7146 |
| Output Tokens | 3775 | 4170 |
| Dollars Spent | $0.07 | $0.07 |

### Memo

Based on the point estimates for pass@1, condition B (gpt‑5.6‑terra) achieved a perfect score of 1.0, while condition A (gpt‑5.6‑luna) achieved 0.9667. On point estimates alone, condition B appears to perform slightly better. However, point estimates alone do not determine whether the difference is meaningful.

The uncertainty intervals provide the evidence needed to interpret the comparison. Condition A’s 95% confidence interval for pass@1 is [0.90, 1.00], while condition B’s interval is [1.00, 1.00]. Because condition B’s interval is a single point at 1.00 and condition A’s interval reaches 1.00, the intervals overlap at the upper bound. This overlap means the evidence does not clearly separate the two conditions. Therefore, **The evidence does not support a ranking.**

An important external‑validity limitation is that CS690‑Eval20 contains only 20 small Python problems. These problems are intentionally simple and self‑contained, and they do not represent the full complexity of real software engineering tasks. Real projects involve multi‑file structure, debugging, ambiguous requirements, integration with external systems, and long‑context reasoning.

A likely source of variance in this experiment is the sampling process. Both models were run at temperature 1.0 with no seed, meaning each attempt is a fresh random draw. Even small changes in sampling can produce different code paths, errors, or successes. Additionally, the small number of tasks amplifies variance: with only 20 tasks, a few successes or failures can shift the score noticeably.

Because of these factors, a rerun of the experiment — or a classmate’s run — will produce slightly different numbers. The harness records all settings, prompts, and returned model versions, so the experiment is reproducible in structure, but not identical in outcomes due to sampling.

---

## Part 5. Reading a published score

**Benchmark chosen:** HumanEval

HumanEval measures the ability to write short Python functions that satisfy hidden unit tests. Each problem provides a function signature and a natural‑language description of the expected behavior. The benchmark evaluates whether the generated code passes the tests. In other words, HumanEval measures single‑function correctness under hidden tests.

HumanEval does not measure several important aspects of real‑world programming. It does not test reading existing codebases, integrating with libraries, handling ambiguous requirements, or maintaining state across multiple files. It also does not test performance, security, or robustness. Because the tasks are short and self‑contained, a model can perform well on HumanEval without being capable of handling realistic development tasks.

A reported HumanEval score can rise without the underlying model truly improving. Prompt engineering, better sampling strategies, or improved test‑passing heuristics can increase the score. Additionally, models may learn patterns from similar problems in training data, which can inflate performance without reflecting genuine reasoning improvements.

Contamination is a known concern. HumanEval was released publicly, and many of its problems have circulated widely in tutorials, GitHub repositories, and model‑training corpora. Several papers have documented contamination risks, and some models have been shown to memorize solutions. Because contamination cannot be ruled out, HumanEval scores must be interpreted cautiously.

HumanEval’s score is not interchangeable with CS690‑Eval20. HumanEval uses hidden tests, while CS690‑Eval20 uses visible tests and fixed prompts. HumanEval tasks are widely known, while CS690‑Eval20 is a small, course‑specific benchmark. The two measure different aspects of model behavior, and results from one cannot be used to infer performance on the other.

---

## References

*(No external references required beyond the benchmark’s primary paper and course materials.)*

---
