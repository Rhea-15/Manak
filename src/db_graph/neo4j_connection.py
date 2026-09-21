from neo4j import GraphDatabase


NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "manak_password"


driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)


def verify_connection():
    with driver.session() as session:
        result = session.run("RETURN 'MANAK Neo4j Connected' AS message")
        return result.single()["message"]


if __name__ == "__main__":
    print(verify_connection())
    driver.close()