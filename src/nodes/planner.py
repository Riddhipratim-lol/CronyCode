import logging
from src.state import AgentState
from src.schemas import SolutionPlanResult
from src.llm import pro_service

logger = logging.getLogger("cronycode.nodes.planner")

SYSTEM_PROMPT = """You are a Principal Algorithm Strategist.

Your job is to design a high-quality algorithmic strategy to solve a Data Structures and Algorithms (DSA) problem.
You are given the original problem statement and its structured understanding.

Your task is to produce a detailed solution plan containing:
1. Chosen Algorithm: The name/style of the selected approach (e.g., 'Two Pointers with Hash Map', 'DFS with Backtracking', 'Segment Tree').
2. Time Complexity: Big-O notation with detailed breakdown.
3. Space Complexity: Big-O notation with detailed breakdown.
4. Justification: A detailed explanation of why this algorithm is correct and why it is the most optimal under the specified constraints. Compare it briefly with sub-optimal strategies (e.g., why a brute force O(N^2) would Time Limit Exceeded (TLE), and why this O(N) or O(N log N) approach is required).
5. Failure Modes: Specific risks or pitfalls of the strategy (e.g., recursion stack overflow if depth is large, integer overflow in Python, off-by-one errors in binary search range, TLE if constant factor is too high).
6. Edge Case Considerations: Concrete ways to handle the edge cases listed in the problem understanding.
7. Implementation Guidance: A step-by-step logic guide/blueprint for the implementation. It should be descriptive and logical (e.g., '1. Initialize two pointers at start and end...', '2. Loop while start < end...', '3. In each step...').

CRITICAL WARNING: You MUST NOT generate any Python code or code blocks in your output. Your response must be pure explanation and logic. Leave the implementation entirely to the Code Architect.
"""

def plan_solution(state: AgentState) -> dict:
    """Creates an algorithmic solution blueprint based on the structured problem understanding."""
    problem_statement = state.get("problem_statement", "").strip()
    understanding = state.get("understanding")
    logger.info("Executing Solution Planner node...")

    if not understanding:
        raise ValueError("Problem understanding is missing from the state.")

    user_prompt = f"""Problem Statement:
{problem_statement}

Structured Understanding:
- Category: {understanding.category}
- Input Format: {understanding.input_format}
- Output Format: {understanding.output_format}
- Constraints: {understanding.constraints}
- Edge Cases: {understanding.edge_cases}
- Hidden Assumptions: {understanding.hidden_assumptions}
- Algorithmic Observations: {understanding.algorithmic_observations}
"""

    try:
        plan_result = pro_service.get_structured_output(
            schema=SolutionPlanResult,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt
        )
        logger.info(f"Solution planning complete. Selected algorithm: {plan_result.chosen_algorithm}")
        return {"solution_plan": plan_result}
    except Exception as e:
        logger.error(f"Solution Planner failed during LLM execution: {e}")
        # Build a safe error fallback result
        fallback_result = SolutionPlanResult(
            chosen_algorithm="Unknown/None",
            time_complexity="N/A",
            space_complexity="N/A",
            justification=f"Planning failed due to LLM error: {str(e)}",
            failure_modes=[f"LLM execution error: {str(e)}"],
            edge_case_considerations=[],
            implementation_guidance="Could not generate guidance due to LLM error."
        )
        return {"solution_plan": fallback_result, "error_message": f"LLM error: {str(e)}"}
