from src.backend.cache import cache_get, cache_set
from src.db_graph.neo4j_connection import driver

GRAPH_CACHE_TTL = 60


def get_standard_graph(standard_number: str):
    cache_key = f"manak:graph:{standard_number}"

    cached = cache_get(cache_key)

    if cached is not None:
        return cached

    query = """
    MATCH (s:Standard {standard_number: $standard_number})
    OPTIONAL MATCH (s)-[r]->(linked:Standard)

    RETURN
        s.standard_number AS standard_number,
        s.title AS title,
        collect({
            standard_number: linked.standard_number,
            title: linked.title,
            relationship: type(r)
        }) AS linked_standards
    """

    with driver.session() as session:
        result = session.run(
            query,
            standard_number=standard_number,
        )

        record = result.single()

        if not record:
            response = {
                "found": False,
                "standard_number": standard_number,
                "linked_standards": [],
            }
        else:
            linked_standards = [
                item
                for item in record["linked_standards"]
                if item["standard_number"] is not None
            ]

            response = {
                "found": True,
                "standard_number": record["standard_number"],
                "title": record["title"],
                "linked_standards": linked_standards,
            }

    cache_set(
        cache_key,
        response,
        ttl=GRAPH_CACHE_TTL,
    )

    return response
