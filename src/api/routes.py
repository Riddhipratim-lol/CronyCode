import logging
from fastapi import APIRouter, HTTPException
from src.schemas import SolveRequest, FinalResponsePayload
from src.graph import app as graph_app

logger = logging.getLogger("cronycode.api.routes")
router = APIRouter()

@router.post("/solve", response_model=FinalResponsePayload)
async def solve_problem(request: SolveRequest):
    """Processes a raw problem statement through the LangGraph DSA-solving pipeline."""
    logger.info("Received new problem solving request.")
    
    if not request.problem_statement.strip():
        raise HTTPException(status_code=400, detail="Problem statement cannot be empty.")
    
    try:
        # Construct the initial graph state
        initial_state = {
            "problem_statement": request.problem_statement,
            "classification": None,
            "understanding": None,
            "solution_plan": None,
            "generated_code": None,
            "final_response": None,
            "error_message": None
        }
        
        logger.info("Invoking LangGraph workflow asynchronously...")
        # Invoke compiled LangGraph
        final_state = await graph_app.ainvoke(initial_state)
        
        final_response = final_state.get("final_response")
        if not final_response:
            logger.error("Workflow completed but final_response was missing from state.")
            raise HTTPException(
                status_code=500,
                detail="Workflow execution ended without producing a final response payload."
            )
            
        logger.info(f"Workflow completed successfully with status: {final_response.status}")
        return final_response
        
    except Exception as e:
        logger.exception("Failure in solving pipeline endpoint")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while running the solver pipeline: {str(e)}"
        )

@router.get("/health")
def health_check():
    """Simple service health status endpoint."""
    return {"status": "ok", "service": "DSA Solver MVP"}
