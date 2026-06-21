import logging
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.schemas import SolveRequest, FinalResponsePayload
from src.graph import app as graph_app

logger = logging.getLogger("cronycode.api.routes")
router = APIRouter()

def serialize_value(v):
    """Recursively serializes Pydantic models and other values to JSON-compatible types."""
    if isinstance(v, BaseModel):
        return v.model_dump()
    if isinstance(v, dict):
        return {k: serialize_value(val) for k, val in v.items()}
    if isinstance(v, list):
        return [serialize_value(val) for val in v]
    return v

@router.post("/solve")
async def solve_problem(request: SolveRequest):
    """Processes a raw problem statement through the LangGraph DSA-solving pipeline.
    
    Supports both traditional one-shot JSON responses and streamed line-delimited JSON updates.
    """
    logger.info("Received new problem solving request.")
    
    if not request.problem_statement.strip():
        raise HTTPException(status_code=400, detail="Problem statement cannot be empty.")
    
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

    if request.stream:
        async def event_generator():
            try:
                logger.info("Invoking LangGraph workflow stream...")
                async for update in graph_app.astream(initial_state, stream_mode="updates"):
                    # Serialize the update dictionary containing node name -> state updates
                    serialized_update = serialize_value(update)
                    yield json.dumps(serialized_update) + "\n"
            except Exception as e:
                logger.exception("Failure in solving pipeline streaming execution")
                error_data = {"error": f"An error occurred while streaming the solver pipeline: {str(e)}"}
                yield json.dumps(error_data) + "\n"

        return StreamingResponse(event_generator(), media_type="application/x-ndjson")

    try:
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
