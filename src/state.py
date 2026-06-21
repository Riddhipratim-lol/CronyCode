from typing import Optional
from typing_extensions import TypedDict
from src.schemas import (
    InputClassificationResult,
    ProblemUnderstandingResult,
    SolutionPlanResult,
    CodeArchitectResult,
    FinalResponsePayload,
)

class AgentState(TypedDict):
    """The shared state dictionary for the LangGraph workflow.
    
    Serves as the single source of truth during execution.
    """
    problem_statement: str
    classification: Optional[InputClassificationResult]
    understanding: Optional[ProblemUnderstandingResult]
    solution_plan: Optional[SolutionPlanResult]
    generated_code: Optional[CodeArchitectResult]
    final_response: Optional[FinalResponsePayload]
    error_message: Optional[str]
