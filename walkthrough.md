# Walkthrough - DSA Solver MVP

The DSA Solver MVP is a simplified core reasoning pipeline built using FastAPI, LangGraph, LangChain, and Pydantic. It successfully processes raw algorithmic problem statements, filters out non-DSA inputs, structures the problem analysis, plans a strategy, and implements the final Python code, with a centralized LLM fallback layer.

## Changes Made

### 1. Data Schemas & State Definition
- [schemas.py](file:///Users/riddhipratim/Projects/CronyCode/src/schemas.py): Defined Pydantic models for structured output validation across all nodes:
  - `InputClassificationResult`
  - `ProblemUnderstandingResult`
  - `SolutionPlanResult`
  - `CodeArchitectResult`
  - `FinalResponsePayload`
- [state.py](file:///Users/riddhipratim/Projects/CronyCode/src/state.py): Configured `AgentState` TypedDict to serve as the graph's single source of truth.

### 2. Central LLM Failover Service
- [llm.py](file:///Users/riddhipratim/Projects/CronyCode/src/llm.py): Implemented the `ModelService` utility that supports structured output extraction.
  - Automatically intercepts API errors, rate limits (like the quota limit of 0 on Gemini 2.5 Pro), and timeouts.
  - Automatically falls back from `gemini-2.5-pro` to `gemini-2.5-flash` (or vice-versa) for resiliency.

### 3. Pipeline Nodes
- [input_classifier.py](file:///Users/riddhipratim/Projects/CronyCode/src/nodes/input_classifier.py): Classifies problem statements as DSA or non-DSA.
- [understanding.py](file:///Users/riddhipratim/Projects/CronyCode/src/nodes/understanding.py): Extracts category, constraints, edge cases, hidden assumptions, and observations.
- [planner.py](file:///Users/riddhipratim/Projects/CronyCode/src/nodes/planner.py): Formulates an algorithmic blueprint without generating code.
- [architect.py](file:///Users/riddhipratim/Projects/CronyCode/src/nodes/architect.py): Converts the planner blueprint into production-ready PEP8 Python code.
- [final_output.py](file:///Users/riddhipratim/Projects/CronyCode/src/nodes/final_output.py): Prepares the final structured `FinalResponsePayload` based on execution state.

### 4. Graph Orchestration
- [graph.py](file:///Users/riddhipratim/Projects/CronyCode/src/graph.py): Wired nodes into a linear StateGraph. Included conditional routing after the classification node to exit early if input is not classified as a DSA problem.

### 5. API Server Setup
- [routes.py](file:///Users/riddhipratim/Projects/CronyCode/src/api/routes.py): Exposed `/api/solve` (run graph workflow) and `/api/health` endpoints.
- [main.py](file:///Users/riddhipratim/Projects/CronyCode/src/main.py): Initialized the FastAPI application and registered router endpoints.

---

## Validation Results

We executed a verification script [test_graph.py](file:///Users/riddhipratim/.gemini/antigravity-ide/brain/8dc52529-2a93-439f-863c-8900d82e1251/scratch/test_graph.py) covering multiple scenarios.

### Scenario 1: Valid DSA Problem (Two Sum)
- **Input**: "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target..."
- **Classifier Action**: Identified as DSA problem (`is_dsa_problem=True`).
- **Failover Triggered**: The `understand` node attempted to invoke `gemini-2.5-pro`. This failed with an HTTP 429 quota error (which is standard behavior for the configured API key). The service automatically intercepted this error and fell back to `gemini-2.5-flash`.
- **Result Status**: `SUCCESS`
- **Output Details**:
  - Identified Category: `Arrays`
  - Selected Algorithm: `Hash Map (or Dictionary) Approach`
  - Space/Time Complexity: `O(N)` / `O(N)`
  - Code: A modular Python `Solution` class with type hints and detailed explanation.

### Scenario 2: Non-DSA Input (Cafe Recommendations & Python Installation)
- **Input**: "Hey, what are some good cafes in Paris for coding? Also, how do I install Python?"
- **Classifier Action**: Identified as non-DSA (`is_dsa_problem=False`).
- **Graph Path**: Routed directly to the final formatting node, skipping subsequent nodes.
- **Result Status**: `REJECTED_NON_DSA`
- **Output Details**: Rejection message: "The input contains two questions... Neither of these questions describes a Data Structures and Algorithms problem..."

## File Directory Map

The following files make up the reasoning pipeline:

```
src/
├── api/
│   ├── __init__.py
│   └── routes.py          <-- FastAPI routes (/api/solve, /api/health)
├── nodes/
│   ├── architect.py       <-- Code Architect node
│   ├── final_output.py    <-- State consolidation and response formatting
│   ├── input_classifier.py <-- Input Classification node
│   ├── planner.py         <-- Solution Planner node
│   └── understanding.py   <-- Problem Understanding node
├── __init__.py
├── graph.py               <-- LangGraph configuration and routing
├── llm.py                 <-- LLM service layer with automatic fallback
├── main.py                <-- FastAPI initialization and entry point
├── schemas.py             <-- Pydantic request and response schemas
└── state.py               <-- Shared LangGraph AgentState TypedDict
```

# Walkthrough - Backend Streaming API Support

We have successfully implemented and verified real-time backend streaming support in the DSA Solver reasoning pipeline. Instead of holding the connection open and responding in one shot, client systems can now stream intermediate state updates as each node of the LangGraph finishes execution.

---

## Changes Made

### 1. Schema Update
- **[schemas.py](file:///Users/riddhipratim/Projects/CronyCode/src/schemas.py)**: Added a `stream: bool = False` parameter to the `SolveRequest` payload class, allowing client callers to request a streamed execution or a traditional one-shot response.

### 2. Router Update
- **[routes.py](file:///Users/riddhipratim/Projects/CronyCode/src/api/routes.py)**: 
  - Handled the conditional execution check: if `request.stream` is `True`, the router triggers streaming execution. If `False` (default), the router executes the original one-shot response model.
  - Implemented `serialize_value(v)` to recursively serialize Pydantic models (via `.model_dump()`), dicts, lists, and base types to ensure smooth JSON serialization of the LangGraph state.
  - Leveraged `graph_app.astream(initial_state, stream_mode="updates")` to execute the reasoning pipeline asynchronously.
  - Returns a `StreamingResponse` with media type `application/x-ndjson` (newline-delimited JSON), yielding a JSON string for each node's completion as it executes.

### 3. Test Script
- **[test_stream.py](file:///Users/riddhipratim/.gemini/antigravity-ide/brain/46eb5da8-842e-43cd-921f-bfa286ad8428/scratch/test_stream.py)**: Created an integration test script using `httpx.AsyncClient` and `ASGITransport` to run the FastAPI app end-to-end and test streaming responses.

---

## Verification Results

We executed the `test_stream.py` script, covering both DSA and non-DSA scenarios. The output shows that updates streamed live to the client as each node completed its execution.

### Scenario 1: Valid DSA Problem (Two Sum)
- **Input**: `"Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target."`
- **Streaming Output Flow**:
  1. **Node `classify` completed!**
     - Emitted classification results (identified as a valid DSA problem with `confidence_score=1.0`).
  2. **Node `understand` completed!**
     - Emitted problem category (`Arrays`), inputs, outputs, constraints, edge cases, and algorithmic observations.
  3. **Node `plan` completed!**
     - Emitted the algorithmic solution strategy (`One-Pass Hash Map`), complexities, justification, and step-by-step logic guidance.
  4. **Node `architect` completed!**
     - Emitted generated Python code implementing the plan, along with variable and structure explanations.
  5. **Node `final_output` completed!**
     - Emitted the final state consolidation containing the status `SUCCESS` and all results.

### Scenario 2: Non-DSA Input
- **Input**: `"Where is the nearest cafe in Berlin? Also, how do I install Python?"`
- **Streaming Output Flow**:
  1. **Node `classify` completed!**
     - Emitted classification results showing `is_dsa_problem: false` with reasoning.
  2. **Node `final_output` completed!**
     - The LangGraph automatically short-circuited/routed past the remaining reasoning nodes directly to `final_output`, yielding the final response status `REJECTED_NON_DSA`.

