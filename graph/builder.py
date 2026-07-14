# graph/builder.py
from langgraph.graph import StateGraph, END
from graph.state import CreatorFinderState
from nodes.intake import intake_node
from nodes.keyword_gen import keyword_gen_node
from nodes.search import search_node
from nodes.enrich import enrich_node


def should_continue(state: CreatorFinderState) -> str:
    """
    After enrich, check if there are more keywords to process.
    If yes, loop back to search. If no, go to END.
    """
    if state["current_keyword_idx"] < len(state["keywords"]):
        return "continue"
    return "done"


def build_graph():
    graph = StateGraph(CreatorFinderState)

    graph.add_node("intake", intake_node)
    graph.add_node("keyword_gen", keyword_gen_node)
    graph.add_node("search", search_node)
    graph.add_node("enrich", enrich_node)

    graph.set_entry_point("intake")
    graph.add_edge("intake", "keyword_gen")
    graph.add_edge("keyword_gen", "search")
    graph.add_edge("search", "enrich")

    # loop: enrich → search (next keyword) or END
    graph.add_conditional_edges(
        "enrich",
        should_continue,
        {
            "continue": "search",
            "done": END
        }
    )

    return graph.compile()