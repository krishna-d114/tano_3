# graph/builder.py
from langgraph.graph import StateGraph, END
from graph.state import CreatorFinderState
from nodes.intake import intake_node
from nodes.keyword_gen import keyword_gen_node


def build_graph():
    graph = StateGraph(CreatorFinderState)

    # register nodes
    graph.add_node("intake", intake_node)
    graph.add_node("keyword_gen", keyword_gen_node)

    # edges
    graph.set_entry_point("intake")
    graph.add_edge("intake", "keyword_gen")
    graph.add_edge("keyword_gen", END)

    return graph.compile()