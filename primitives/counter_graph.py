from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, START, END
import operator

class CounterState(TypedDict):
    count: int
    history: Annotated[list[str], operator.add]
    status: str


def increment_node(state: CounterState) -> dict:
    new_count = state['count'] + 1
    print(f"  [INCREMENT] {state['count']} → {new_count}")

    return {
        "count": new_count,
        "history": [f"Incremented to {new_count}"],
        "status":"incremented"
    }

def double_node(state: CounterState) -> dict:
    new_count = state['count'] * 2
    print(f"  [DOUBLE] {state['count']} → {new_count}")

    return {
        "count": new_count,
        "history": [f"Doubled to {new_count}"],
        "status":"doubled"
    }

def check_node(state: CounterState) -> dict:
    count = state["count"]
    should_continue = count < 10
    print(f" [CHECK] Count is {count}, continue: {should_continue}")
    return {
        "status": "continue" if should_continue else "done"
    }

def route_after_check(state: CounterState) -> Literal["increment", "end"]:
    if state["status"] == "continue":
        return "increment"
    else:
        return "end"


def create_counter_graph():
    """
    Constructs the graph:
    
    START → increment → double → check → (loop back to increment OR end)
    """
    # Initialize with the state schema
    graph = StateGraph(CounterState)
    
    # Add nodes (name → function)
    graph.add_node("increment", increment_node)
    graph.add_node("double", double_node)
    graph.add_node("check", check_node)
    
    # Add edges
    graph.add_edge(START, "increment")      # Start here
    graph.add_edge("increment", "double")   # Regular edge: always goes here
    graph.add_edge("double", "check")       # Regular edge
    
    # Conditional edge: route based on state
    graph.add_conditional_edges(
        "check",                  # From this node
        route_after_check,        # Use this function to decide
        {
            "increment": "increment",  # If returns "increment", go to increment node
            "end": END                 # If returns "end", stop
        }
    )
    
    # Compile into a runnable
    return graph.compile()


# ==============================================================================
# 5. RUN THE GRAPH
# ==============================================================================

def main():
    print("=== LangGraph Primitives Demo ===\n")
    
    # Create the graph
    app = create_counter_graph()
    
    # Initial state
    initial_state = {
        "count": 1,
        "history": ["Started with 1"],
        "status": "initialized"
    }
    
    print("Initial state:", initial_state)
    print("\nRunning graph...\n")
    
    # Execute the graph
    # .invoke() runs the entire graph from start to finish
    final_state = app.invoke(initial_state)
    
    print("\n=== Final State ===")
    print(f"Count: {final_state['count']}")
    print(f"Status: {final_state['status']}")
    print(f"History: {final_state['history']}")


if __name__ == "__main__":
    main()

