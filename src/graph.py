import logging
from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from src.nodes.input_classifier import classify_input
from src.nodes.understanding import understand_problem
from src.nodes.planner import plan_solution
from src.nodes.architect import architect_code
from src.nodes.final_output import format_final_output

logger = logging.getLogger("cronycode.graph")

def check_dsa_classification(state: AgentState) -> str:
    """Router function that evaluates classification result to decide the path."""
    classification = state.get("classification")
    if classification and classification.is_dsa_problem:
        logger.info("Input classified as DSA problem. Routing to Problem Understanding.")
        return "understand"
    
    logger.info("Input classified as Non-DSA problem. Routing directly to Final Output.")
    return "final_output"

# Define the StateGraph with our AgentState dictionary
workflow = StateGraph(AgentState)

# Add all process nodes
workflow.add_node("classify", classify_input)
workflow.add_node("understand", understand_problem)
workflow.add_node("plan", plan_solution)
workflow.add_node("architect", architect_code)
workflow.add_node("final_output", format_final_output)

# Set the entry point of the workflow
workflow.add_edge(START, "classify")

# Add conditional routing after input classification
workflow.add_conditional_edges(
    "classify",
    check_dsa_classification,
    {
        "understand": "understand",
        "final_output": "final_output"
    }
)

# Linear flow for valid DSA problems
workflow.add_edge("understand", "plan")
workflow.add_edge("plan", "architect")
workflow.add_edge("architect", "final_output")

# Set the exit point
workflow.add_edge("final_output", END)

# Compile the workflow
app = workflow.compile()
