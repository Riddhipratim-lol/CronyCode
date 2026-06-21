import logging
from src.state import AgentState
from src.schemas import InputClassificationResult
from src.llm import flash_service

logger = logging.getLogger("cronycode.nodes.input_classifier")

SYSTEM_PROMPT = """You are a Data Structures and Algorithms (DSA) expert and input classifier.

Your task is to analyze the user's input and determine whether it represents a valid, complete Data Structures and Algorithms (DSA) problem statement.

A valid DSA problem description typically contains:
1. A clear task definition or query (e.g., 'find the shortest path', 'sort the array', 'find the maximum sum subarray', 'detect a cycle in a graph').
2. Explicit or implicit input/output expectations.
3. Often (but not strictly required) constraints or data structure definitions.

You MUST reject:
1. Casual conversations, greetings, or off-topic chat (e.g., 'Hello', 'How are you?', 'Who are you?').
2. Unrelated text, garbage characters, noise, or malformed inputs.
3. General programming or system configuration questions that are not algorithmic challenges (e.g., 'How do I install Python?', 'Explain object-oriented programming', 'Write a flask server', 'How to debug a syntax error').
4. Extremely incomplete or vague prompts that do not describe a solvable problem (e.g., 'implement a queue', 'binary search trees', 'recursion').

Provide your response strictly adhering to the schema, specifying if it is a valid DSA problem, your confidence score (0.0 to 1.0), and a detailed reasoning explanation.
"""

def classify_input(state: AgentState) -> dict:
    """Classifies the input problem statement to determine if it is a valid DSA problem."""
    problem_statement = state.get("problem_statement", "").strip()
    logger.info("Executing Input Classification node...")

    if not problem_statement:
        result = InputClassificationResult(
            is_dsa_problem=False,
            confidence_score=1.0,
            reasoning="The problem statement is empty."
        )
        return {"classification": result}

    user_prompt = f"Problem statement to analyze:\n\n{problem_statement}"

    try:
        classification_result = flash_service.get_structured_output(
            schema=InputClassificationResult,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt
        )
        logger.info(
            f"Classification complete: is_dsa_problem={classification_result.is_dsa_problem}, "
            f"confidence={classification_result.confidence_score}"
        )
        return {"classification": classification_result}
    except Exception as e:
        logger.error(f"Input Classification failed during LLM execution: {e}")
        # Build a safe error fallback result
        fallback_result = InputClassificationResult(
            is_dsa_problem=False,
            confidence_score=0.0,
            reasoning=f"System error classification failed due to LLM error: {str(e)}"
        )
        return {"classification": fallback_result, "error_message": f"LLM error: {str(e)}"}
