# High-Level Execution Flow

The execution journey begins when a user submits a raw problem statement into the shared application state. The control flow immediately passes to an **Input Classification Node** that uses structured reasoning to determine whether the provided text represents a valid Data Structures and Algorithms (DSA) challenge.

The classifier distinguishes programming problems from unrelated text, conversational messages, malformed inputs, or incomplete prompts. If the input is classified as non-DSA content, the graph terminates gracefully to conserve computational resources and API costs.

When a valid algorithmic challenge is confirmed, the workflow advances to the **Context Search Engine**.

---

# Tech Stack

Agent Framework:
LangGraph
LangChain

Models:
Gemini 3.5 Flash
Gemini 3.1 Flash-Lite

State:
LangGraph State

Validation:
Pydantic
jsonschema

Execution:
subprocess
tempfile
sys.executable

Search:
Tavily

Configuration:
python-dotenv

Typing:
typing
typing_extensions

---

## Context Search Engine

The Context Search Engine is responsible for enriching the problem statement with authoritative metadata.

This module first analyzes the input for platform-specific identifiers such as:

- LeetCode problem numbers
- Codeforces contest IDs
- CodeChef problem codes
- AtCoder task identifiers
- HackerRank challenges
- HackerEarth problems
- SPOJ identifiers
- Other recognizable competitive programming references

When a known source is detected, the engine performs real-time searches to retrieve:

- Official problem statements
- Constraints
- Time limits
- Memory limits
- Sample inputs and outputs
- Editorial metadata when available

The retrieved information is appended to the shared application state and marked with a source confidence level indicating that the data originated from an official source.

### Search Failure Recovery

External retrieval is not assumed to be reliable.

If a platform is identified but retrieval fails because of:

- Network issues
- Rate limits
- Platform changes
- Invalid identifiers
- Parsing failures

the workflow does not terminate.

Instead, control automatically transitions into the **Constraint Inference Module**.

---

## Constraint Inference Module

When official metadata cannot be obtained—or when no platform identifier exists—the system activates a dedicated inference layer.

This module analyzes the problem description and estimates:

- Input size ranges
- Value ranges
- Expected computational complexity
- Memory expectations
- Typical competitive-programming constraints

All inferred constraints are stored together with a confidence label:

```
OFFICIAL
EXPLICIT
INFERRED_HIGH_CONFIDENCE
INFERRED_LOW_CONFIDENCE
```

These confidence levels later influence optimization decisions and complexity validation.

### Constraint Feedback Integration

Inferred constraints are not treated as final.

If execution evidence gathered during sandbox runs or complexity review contradicts the initial inference—such as timeout behavior inconsistent with the estimated input scale, or memory consumption patterns that suggest a different value range—the system updates the constraint estimates in the shared application state.

This updated inference is propagated to the Complexity Review Node, which re-evaluates the solution against the revised constraints. If a previously accepted solution no longer satisfies the updated bounds, the workflow escalates to the Solution Planner for a constraint-aware redesign.

This ensures that low-confidence inferences do not permanently anchor the workflow to incorrect assumptions.

---

## Problem Understanding Node

Once sufficient context has been assembled, control transitions into the **Problem Understanding Node**.

This node converts the natural-language challenge into a structured representation that downstream agents can reason about consistently.

The generated representation includes:

### Problem Classification

- Arrays
- Strings
- Linked Lists
- Trees
- Graphs
- Dynamic Programming
- Greedy
- Binary Search
- Backtracking
- Bit Manipulation
- Advanced Data Structures

### Structured Problem Model

- Input format
- Output format
- Constraint summary
- Edge conditions
- Hidden assumptions
- Required behaviors

### Algorithmic Observations

The node generates key observations describing:

- What must be computed
- Important invariants
- Candidate patterns
- Potential pitfalls

This structured understanding becomes the canonical problem representation used by all subsequent nodes.

---

## Solution Planning Node

The graph then advances into the **Solution Planning Node**.

This node acts as an algorithm strategist rather than a code generator.

Using:

- Problem understanding
- Constraints
- Confidence levels
- Candidate approaches
- Historical failure context (when available)

The planner evaluates multiple algorithmic strategies and selects the most appropriate one.

During normal execution the planner operates solely on the problem representation and constraints. During replanning cycles, however, it additionally receives execution-derived feedback such as failed test cases, debugger analysis, prior solution blueprints, and performance observations. This allows the planner to avoid previously unsuccessful strategies and generate more informed redesigns.

The planner produces a detailed blueprint containing:

- Chosen algorithm
- Time complexity
- Space complexity
- Design justification
- Failure modes
- Edge-case considerations
- Implementation guidance

By separating planning from implementation, the architecture prevents the coding agent from prematurely committing to suboptimal solutions.

---

## Enhanced Test Case Factory (Phase 1)

Before implementation begins, the workflow enters the first stage of the **Enhanced Test Case Factory**.

This phase generates implementation-independent validation data.

The generated suite includes:

### Standard Validation

- Official examples
- Sample inputs
- Sample outputs

### Functional Validation

- Common scenarios
- Typical usage patterns

### Boundary Validation

- Minimum inputs
- Maximum inputs
- Extreme values

### Edge Cases

- Empty structures
- Singleton collections
- Duplicate values
- Negative values
- Overflow-prone values

### Stress Tests

- Maximum-scale inputs
- Worst-case distributions

### Adversarial Cases

- Off-by-one errors
- Incorrect indexing
- Greedy traps
- Invalid transitions
- Common interview mistakes

All generated test artifacts are validated against a strict schema before entering execution.

This prevents malformed testing contracts from triggering unnecessary debugging cycles.

---

## Code Architect Node

The graph then transitions into the **Code Architect Node**.

Operating as a principal-level software engineer, this node receives:

- Structured problem understanding
- Solution blueprint
- Constraints
- Initial testing contract

The architect's responsibility is implementation rather than algorithm design.

The output is:

- Clean Python code
- Modular structure
- Readable logic
- Deterministic behavior
- Compatibility with execution infrastructure

---

## Enhanced Test Case Factory (Phase 2)

After implementation is generated, the Test Factory performs a second pass.

Unlike the first phase, this pass is implementation-aware.

The node analyzes the generated code and constructs targeted adversarial cases designed to expose:

- Boundary-condition mistakes
- State-transition bugs
- Incorrect assumptions
- Loop termination issues
- Data-structure misuse
- Algorithm-specific vulnerabilities

These additional tests are merged into the existing testing contract before execution begins.

All test artifacts produced in this phase are validated against the same strict schema enforced in Phase 1. If any generated test fails schema validation, it is discarded rather than forwarded to the executor. Execution proceeds with the remaining valid tests. If the merged contract contains no valid tests after this check, the workflow falls back to the Phase 1 suite exclusively.

---

## Sandboxed Execution Node

The generated solution is then forwarded into a secure execution environment.

The executor:

1. Writes generated code to a temporary file.
2. Executes it using `sys.executable`.
3. Supplies test data through stdin.
4. Captures outputs through stdout.

The sandbox enforces:

- Process isolation
- Resource restrictions
- Memory limits
- Timeout limits

A strict two-second timeout is applied to prevent:

- Infinite loops
- Excessive resource consumption
- Runaway executions

The execution report includes:

```
stdout
stderr
runtime exceptions
timeout events
memory usage
runtime metrics
test-level results
```

---

## Failure Analysis and Debugger Node

Whenever validation fails, control is transferred to the **Debugger Node**, provided the global execution budget has not been exhausted. Budget exhaustion is evaluated before the debugger begins any analysis. If the budget is already spent, the workflow skips the debugger entirely and proceeds directly to budget-exhaustion termination.

The debugger receives:

- Source code
- Stack traces
- Runtime logs
- Expected outputs
- Actual outputs
- Failed test metadata

### Failure Classification

The debugger first classifies the failure along two dimensions: the defect origin (implementation versus strategy) and the defect severity (isolated versus systemic). This two-dimensional classification replaces a binary path decision and handles mixed failures explicitly.

A failure is considered mixed when the debugger detects both a strategy-level flaw and implementation-level defects within the same failing execution. In such cases, the debugger does not attempt a targeted fix. Instead, it escalates directly to the Solution Planner with a mixed-failure payload that includes all implementation observations alongside the strategy analysis. This prevents wasting a budget slot on a targeted fix that cannot succeed because the underlying algorithm is also incorrect.

### Path A — Implementation Defect

If the algorithm remains correct but the implementation contains isolated defects:

- Syntax errors
- Runtime exceptions
- Incorrect conditions
- Data structure misuse

the debugger applies targeted fixes and returns control directly to the sandbox.

```
Debugger
   ↓
Sandbox
```

Each targeted fix and subsequent sandbox re-run counts as a single sub-iteration. The debugger is permitted a maximum of two sub-iterations per budget slot before it reclassifies the failure as systemic and escalates to the Solution Planner. This prevents repeated misidentified fixes from silently consuming execution resources without advancing toward a correct solution.

### Path B — Strategy Defect

If the debugger determines that the root cause originates from an incorrect algorithmic strategy rather than coding mistakes—or if the failure is classified as mixed—the workflow escalates.

Examples include:

- Wrong greedy choice
- Incorrect DP formulation
- Invalid graph approach
- Misidentified problem pattern
- Mixed implementation and strategy defects

In such cases, the debugger triggers a replanning cycle. However, the Solution Planner does not receive only the original problem statement. To prevent repeated generation of the same incorrect strategy, the planner is supplied with additional failure context gathered during execution.

The replanning payload includes:

- Original problem understanding
- Previous solution blueprint
- Failed test cases
- Expected versus actual outputs
- Debugger root-cause analysis
- Failure classification (pure strategy defect or mixed)
- Complexity observations when available

This enables the planner to reason about why the previous strategy failed and generate a revised algorithm rather than reproducing the same approach.

The replanning process therefore becomes:

```
Original Plan
       ↓
Failure Analysis
       ↓
Strategy-Aware Replanning
       ↓
New Solution Blueprint
```

By incorporating historical failure information into the planning process, the architecture significantly reduces redundant redesign cycles and improves convergence rates.

---

## Complexity Review Node

Once all functional tests pass successfully, the workflow proceeds into the **Complexity Review Node**.

Before initiating any analysis, the Complexity Review Node queries the global execution budget. If no budget remains for a complexity-driven redesign, the node completes its analysis and produces a complexity assessment but does not escalate to the Solution Planner regardless of the outcome. The solution is forwarded to final output accompanied by a performance-risk warning.

This node serves as a final algorithmic auditor.

Unlike purely static analysis, the reviewer combines:

### Static Analysis

- Time complexity estimation
- Space complexity estimation
- Algorithm structure analysis

### Runtime Evidence

- Actual execution times
- Stress-test performance
- Timeout behavior
- Memory consumption

This hybrid approach enables significantly more reliable performance validation.

---

## Confidence-Aware Optimization Review

When official constraints exist, strict validation is enforced.

If a solution passes correctness tests but is unlikely to satisfy production-scale constraints, it is rejected.

However, when constraints are inferred rather than officially sourced, the reviewer adopts a confidence-aware policy.

Possible outcomes include:

### Accepted

Solution appears safe.

### Accepted With Warning

Solution is correct but may degrade under larger inputs.

### Redesign Required

Solution is highly likely to violate expected limits.

---

## Complexity-Driven Replanning

When performance issues originate from algorithm design rather than implementation quality, and when the global execution budget permits at least one additional correction iteration, the reviewer does not send control back to the Code Architect.

Instead, the workflow returns to the Solution Planner.

```
Complexity Review
        ↓
Solution Planner
        ↓
Code Architect
```

This ensures that complexity failures trigger algorithm redesign rather than superficial code modifications.

---

## Global Execution Budget

To prevent runaway agentic behavior and excessive API consumption, the entire workflow operates under a centralized execution budget.

### Budget Definition

The budget is defined as a single shared pool of three correction iterations. A correction iteration is consumed by any one of the following events:

- A debugger escalation to the Solution Planner (Path B or mixed failure)
- A complexity-driven escalation to the Solution Planner
- A targeted debugger fix cycle (Path A) that reaches its two sub-iteration sub-limit and is subsequently reclassified as a strategy defect

Targeted fix sub-iterations within a single Path A cycle do not each consume a budget slot. Only the cycle as a whole consumes one slot upon escalation. This distinction ensures that minor implementation defects resolved quickly do not penalize the budget unnecessarily.

The Complexity Review Node and the Debugger Node both check the remaining budget before initiating any escalation. Neither node may initiate a replanning cycle if the budget pool is empty.

### Exhaustion Behavior

If convergence is not achieved within this budget, execution terminates automatically.

The solution selected for return is not simply the most recent one. The workflow tracks a best-candidate record throughout execution, updated whenever a solution achieves a higher test pass rate than the previous best. Upon budget exhaustion, the best-candidate record is returned rather than the final incomplete attempt.

The termination response contains:

- Best-candidate Python implementation
- Test results achieved by the best candidate
- Failure diagnostics from the final attempt
- Complexity assessment
- Remaining risks
- Constraint confidence assessment

This guarantees predictable costs and bounded execution time while maximizing the quality of the fallback response.

---

## Final Output

The graph reaches completion only when a solution satisfies both:

1. Functional correctness
2. Performance requirements proportional to constraint confidence

The final response contains:

- Verified Python implementation
- Complete execution report
- Test coverage summary
- Time complexity analysis
- Space complexity analysis
- Optimization recommendations
- Constraint confidence assessment
- Performance-risk warnings
- Concise algorithm explanation