# nodes/intake.py
from graph.state import CreatorFinderState


def intake_node(state: CreatorFinderState) -> dict:
    """
    Node 1: Initializes the pipeline state from user inputs.
    No API calls, just state setup.
    """
    print("\n--- NODE 1: INTAKE ---")
    print(f"Product : {state['product_description']}")
    print(f"Budget  : {state['budget_tier']}")
    print(f"Location: {state['location']}")

    return {
        "current_keyword_idx": 0,
        "current_batch_channel_ids": [],
        "candidates": {},
        "shortlist": [],
        "error": "",
    }