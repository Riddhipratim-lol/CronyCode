from typing import List, Optional
from pydantic import BaseModel, Field

class SolveRequest(BaseModel):
    """Payload format for the solve endpoint request."""
    problem_statement: str = Field(..., description="The raw problem statement text of the DSA challenge.")

class InputClassificationResult(BaseModel):
    """Output schema for the Input Classification node."""
    is_dsa_problem: bool = Field(
        ..., 
        description="True if the input is a valid Data Structures and Algorithms (DSA) problem, False otherwise."
    )
    confidence_score: float = Field(
        ..., 
        description="Confidence score between 0.0 and 1.0 of the classification decision."
    )
    reasoning: str = Field(
        ..., 
        description="Detailed justification explaining the classification choice."
    )

class ProblemUnderstandingResult(BaseModel):
    """Output schema for the Problem Understanding node."""
    category: str = Field(
        ..., 
        description="Primary problem category (e.g., Arrays, Strings, Linked Lists, Trees, Graphs, Dynamic Programming, Greedy, Binary Search, Backtracking, Bit Manipulation, etc.)."
    )
    input_format: str = Field(
        ..., 
        description="Structured representation of the input parameters and their formats."
    )
    output_format: str = Field(
        ..., 
        description="Structured representation of the expected output format."
    )
    constraints: List[str] = Field(
        default_factory=list, 
        description="List of performance, value, or size constraints mentioned or implied."
    )
    edge_cases: List[str] = Field(
        default_factory=list, 
        description="Identified edge cases (e.g., empty inputs, single element, negative values, boundary values)."
    )
    hidden_assumptions: List[str] = Field(
        default_factory=list, 
        description="Inferred or hidden assumptions not explicitly stated but required for correctness."
    )
    algorithmic_observations: List[str] = Field(
        default_factory=list, 
        description="Key observations that help design the algorithm (e.g., monotonicity, structure properties)."
    )

class SolutionPlanResult(BaseModel):
    """Output schema for the Solution Planner node."""
    chosen_algorithm: str = Field(
        ..., 
        description="Name of the selected algorithmic approach."
    )
    time_complexity: str = Field(
        ..., 
        description="Big-O notation of expected time complexity."
    )
    space_complexity: str = Field(
        ..., 
        description="Big-O notation of expected space complexity."
    )
    justification: str = Field(
        ..., 
        description="Reasoning explaining why this specific algorithm is optimal under the constraints."
    )
    failure_modes: List[str] = Field(
        default_factory=list, 
        description="Potential failure points (e.g., stack overflow, integer overflow, TLE risks)."
    )
    edge_case_considerations: List[str] = Field(
        default_factory=list, 
        description="Specific strategy to handle the identified edge cases."
    )
    implementation_guidance: str = Field(
        ..., 
        description="Step-by-step logic guide for implementation, without providing any code."
    )

class CodeArchitectResult(BaseModel):
    """Output schema for the Code Architect node."""
    code: str = Field(
        ..., 
        description="Clean, PEP8-compliant, modular Python code implementing the plan."
    )
    explanation: str = Field(
        ..., 
        description="Brief description of the implementation structure, variable naming, and efficiency."
    )

class FinalResponsePayload(BaseModel):
    """Output payload for the final response API response."""
    status: str = Field(
        ..., 
        description="Overall execution status. E.g., 'SUCCESS', 'REJECTED_NON_DSA', 'ERROR'."
    )
    message: str = Field(
        ..., 
        description="Summary or message explaining the status."
    )
    classification: InputClassificationResult = Field(
        ..., 
        description="The detailed results from the Input Classifier."
    )
    understanding: Optional[ProblemUnderstandingResult] = Field(
        None, 
        description="Structured representation of the problem. None if classification rejected."
    )
    solution_plan: Optional[SolutionPlanResult] = Field(
        None, 
        description="Algorithm blueprint details. None if classification rejected."
    )
    generated_code: Optional[CodeArchitectResult] = Field(
        None, 
        description="The final implemented Python code. None if classification rejected."
    )
