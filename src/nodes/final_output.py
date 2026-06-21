import logging
from src.state import AgentState
from src.schemas import FinalResponsePayload

logger = logging.getLogger("cronycode.nodes.final_output")

def format_final_output(state: AgentState) -> dict:
    """Formats the final response payload based on the accumulated graph state."""
    logger.info("Executing Final Output formatting node...")
    classification = state.get("classification")
    error_message = state.get("error_message")

    # If classification doesn't exist (unexpected, but handle safely)
    if not classification:
        payload = FinalResponsePayload(
            status="ERROR",
            message="Input classification was not performed.",
            classification=None
        )
        return {"final_response": payload}

    # Case 1: Classified as Non-DSA
    if not classification.is_dsa_problem:
        payload = FinalResponsePayload(
            status="REJECTED_NON_DSA",
            message=f"Rejection reason: {classification.reasoning}",
            classification=classification,
            understanding=None,
            solution_plan=None,
            generated_code=None
        )
        logger.info("Final response generated: Rejected (Non-DSA).")
        return {"final_response": payload}

    # Case 2: Technical Error occurred during execution
    if error_message:
        payload = FinalResponsePayload(
            status="ERROR",
            message=f"Workflow failed: {error_message}",
            classification=classification,
            understanding=state.get("understanding"),
            solution_plan=state.get("solution_plan"),
            generated_code=state.get("generated_code")
        )
        logger.info("Final response generated: Error occurred.")
        return {"final_response": payload}

    # Case 3: Success
    payload = FinalResponsePayload(
        status="SUCCESS",
        message="Algorithm solution and implementation generated successfully.",
        classification=classification,
        understanding=state.get("understanding"),
        solution_plan=state.get("solution_plan"),
        generated_code=state.get("generated_code")
    )
    logger.info("Final response generated: Success.")
    return {"final_response": payload}
