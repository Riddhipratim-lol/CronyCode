import logging
from src.state import AgentState
from src.schemas import CodeArchitectResult
from src.llm import pro_service

logger = logging.getLogger("cronycode.nodes.architect")

SYSTEM_PROMPT = """You are a Senior Python Developer and Code Architect.

Your task is to convert a structured problem understanding and a detailed solution blueprint (planning blueprint) into clean, production-ready Python code.

You must follow these rules strictly:
1. FAITHFULLY IMPLEMENT THE PLAN: Do not redesign the algorithm or introduce alternative strategies. You must implement the chosen algorithm and guidance described in the solution plan exactly.
2. PRODUCTION QUALITY: Write clean, readable, modular Python code. Use PEP8 styling.
3. TYPING & DOCUMENTATION: Provide type hints for all parameters and return types. Add a docstring to the class/functions explaining inputs, outputs, and behavior.
4. MEANINGFUL NAMES: Use descriptive and meaningful variable and function names. Avoid single-character names except for loop indices.
5. NO WRAPPING MARKDOWN: Do not wrap the code field inside markdown blocks (e.g., ```python ... ```). Write the raw python code directly into the code string parameter.
6. COMMENTS: Add brief, clear comments explaining non-obvious lines of logic.
"""

def architect_code(state: AgentState) -> dict:
    """Implements the final Python code based on the problem understanding and solution plan."""
    problem_statement = state.get("problem_statement", "").strip()
    understanding = state.get("understanding")
    solution_plan = state.get("solution_plan")
    logger.info("Executing Code Architect node...")

    if not understanding or not solution_plan:
        raise ValueError("Problem understanding or solution plan is missing from the state.")

    user_prompt = f"""Problem Statement:
{problem_statement}

Problem Understanding:
- Category: {understanding.category}
- Input Format: {understanding.input_format}
- Output Format: {understanding.output_format}
- Constraints: {understanding.constraints}

Solution Blueprint:
- Algorithm: {solution_plan.chosen_algorithm}
- Time Complexity: {solution_plan.time_complexity}
- Space Complexity: {solution_plan.space_complexity}
- Edge Case Considerations: {solution_plan.edge_case_considerations}
- Implementation Guidance: {solution_plan.implementation_guidance}
"""

    try:
        architect_result = pro_service.get_structured_output(
            schema=CodeArchitectResult,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt
        )
        logger.info("Code architecture complete.")
        return {"generated_code": architect_result}
    except Exception as e:
        logger.error(f"Code Architect failed during LLM execution: {e}")
        # Build a safe error fallback result
        fallback_result = CodeArchitectResult(
            code="# Code generation failed due to LLM error.",
            explanation=f"Architecture execution failed: {str(e)}"
        )
        return {"generated_code": fallback_result, "error_message": f"LLM error: {str(e)}"}
