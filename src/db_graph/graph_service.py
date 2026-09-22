from src.db_graph.neo4j_connection import driver


def get_standard_graph(standard_number: str):
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
        result = session.run(query, standard_number=standard_number)

        record = result.single()

        if not record:
            return {
                "found": False,
                "standard_number": standard_number,
                "linked_standards": [],
            }

        linked_standards = [
            item
            for item in record["linked_standards"]
            if item["standard_number"] is not None
        ]

        return {
            "found": True,
            "standard_number": record["standard_number"],
            "title": record["title"],
            "linked_standards": linked_standards,
        }
