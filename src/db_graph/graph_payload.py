from src.db_graph.graph_service import get_standard_graph


def build_graph_payload(standard_number: str):
    graph = get_standard_graph(standard_number)

    return {
        "graph": {
            "found": graph.get("found", False),
            "standard_number": graph.get("standard_number"),
            "title": graph.get("title"),
            "linked_standards": graph.get("linked_standards", []),
        }
    }
