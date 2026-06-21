import logging
from src.state import AgentState
from src.schemas import ProblemUnderstandingResult
from src.llm import pro_service

logger = logging.getLogger("cronycode.nodes.understanding")

SYSTEM_PROMPT = """You are a Senior Algorithm Analyst specializing in Data Structures and Algorithms (DSA).

Your task is to analyze a raw DSA problem statement and produce a structured, high-quality analysis representation.
You must extract and synthesize:
1. Category: Identify the primary category of the problem (e.g., Arrays, Strings, Linked Lists, Trees, Graphs, Dynamic Programming, Greedy, Binary Search, Backtracking, Bit Manipulation, etc.).
2. Input Format: A clear representation of the parameters, data types, and structures provided.
3. Output Format: The format and type of the expected result.
4. Constraints: A list of value ranges, size bounds (e.g., length of arrays, number of nodes), time/memory limits, or efficiency expectations.
5. Edge Cases: Critical scenarios to consider (e.g., empty arrays, single elements, negative integers, duplicate values, boundary bounds, extreme inputs).
6. Hidden Assumptions: Inferred behaviors or properties not explicitly stated but necessary for correctness (e.g., 'the array is sorted', 'the graph is a DAG', 'integer division truncates towards zero').
7. Algorithmic Observations: Key insights or structural properties about the problem that will aid in designing an efficient solution (e.g., 'the problem is equivalent to finding the shortest path in a weighted graph', 'N <= 10^5 constraints suggest a time complexity of O(N) or O(N log N)').

Ensure your output matches the schema fields exactly. Do not generate code in this node; focus entirely on problem analysis.
"""

def understand_problem(state: AgentState) -> dict:
    """Analyzes the raw problem statement and populates a structured ProblemUnderstandingResult."""
    problem_statement = state.get("problem_statement", "").strip()
    logger.info("Executing Problem Understanding node...")

    user_prompt = f"Problem statement to analyze:\n\n{problem_statement}"

    try:
        understanding_result = pro_service.get_structured_output(
            schema=ProblemUnderstandingResult,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt
        )
        logger.info(f"Problem understanding complete. Category identified: {understanding_result.category}")
        return {"understanding": understanding_result}
    except Exception as e:
        logger.error(f"Problem Understanding failed during LLM execution: {e}")
        # Build a safe error fallback result
        fallback_result = ProblemUnderstandingResult(
            category="Unknown",
            input_format="Extraction failed due to LLM error.",
            output_format="Extraction failed due to LLM error.",
            constraints=[f"LLM execution error: {str(e)}"],
            edge_cases=[],
            hidden_assumptions=[],
            algorithmic_observations=[]
        )
        return {"understanding": fallback_result, "error_message": f"LLM error: {str(e)}"}
