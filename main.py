# main.py
from graph.builder import build_graph

def main():
    graph = build_graph()

    initial_state = {
        "product_description": "An AI-powered fitness app for busy professionals",
        "budget_tier": "mid",       # low | mid | high
        "location": "United States",
    }

    print("=== CREATOR FINDER ===")
    result = graph.invoke(initial_state)

    print("\n=== RESULT ===")
    print(f"Keywords: {result.get('keywords', [])}")
    if result.get("error"):
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    main()