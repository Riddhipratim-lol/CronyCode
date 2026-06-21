# Project Progress - DSA Solver MVP

This file tracks the current state, implemented features, and file structure of the DSA Solver project.

## Current State: Phase 1 (MVP Reasoning Pipeline) Completed

We have established the core reasoning pipeline that converts raw algorithmic problem statements into structured solutions and working Python code. No loops, retries, or execution sandboxes are configured in this version, representing a clean, linear workflow.

### Key Features Implemented
1. **Pydantic Validation Layer**: Structured schemas enforce strict output types for each reasoning agent step.
2. **Central LLM Fallback (Service Layer)**: Centralized orchestration for Gemini API execution. Automatically switches from `gemini-2.5-pro` to `gemini-2.5-flash` (or vice-versa) when technical issues (rate limits/quota limits/timeouts) arise.
3. **Reasoning Graph (LangGraph)**:
   - **Input Classification Node**: Uses Gemini 2.5 Flash to filter out casual conversations, garbage input, or general programming queries.
   - **Problem Understanding Node**: Uses Gemini 2.5 Pro to break down categories, inputs, outputs, constraints, edge cases, and algorithmic observations.
   - **Solution Planner Node**: Uses Gemini 2.5 Pro to design optimal algorithms and complexes without writing code.
   - **Code Architect Node**: Uses Gemini 2.5 Pro to write clean, PEP8, modular, commented Python implementation.
   - **Final Output Node**: Consolidates state variables into a structured output payload.
4. **FastAPI Web Server**: Exposes REST endpoints to query the workflow from client interfaces.

---

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

---

## Running the MVP

### Starting the Server
Run the FastAPI application from the project root:
```bash
.venv/bin/uvicorn src.main:app --reload --port 8000
```

### API Endpoint Usage

#### 1. Submit a DSA Problem
- **Endpoint**: `POST /api/solve`
- **Request Body**:
  ```json
  {
    "problem_statement": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target..."
  }
  ```
- **Response**: Returns a JSON object matching `FinalResponsePayload` containing status, classification, understanding, solution blueprint, and final python code.

#### 2. Health Check
- **Endpoint**: `GET /api/health`
- **Response**:
  ```json
  {
    "status": "ok",
    "service": "DSA Solver MVP"
  }
  ```
