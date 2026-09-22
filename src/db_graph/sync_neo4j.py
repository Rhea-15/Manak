from neo4j import GraphDatabase

from src.backend.database import SessionLocal
from src.db_graph.models import (
    Standard,
    StandardRelationship,
    StandardVersion,
)

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "manak_password"


def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def _is_session_like(obj):
    return hasattr(obj, "run")


def cleanup_removed_standards(tx, postgres_standard_numbers):
    query = """
        MATCH (s:Standard)
        WHERE NOT s.standard_number IN $standard_numbers
        DETACH DELETE s
        RETURN count(s) AS deleted
    """

    if _is_session_like(tx):
        result = tx.run(query, standard_numbers=postgres_standard_numbers)

        record = result.single()

        if record is None:
            return 0

        try:
            return record["deleted"]
        except (KeyError, IndexError, TypeError):
            return 0

    with tx.session() as session:
        result = session.run(query, standard_numbers=postgres_standard_numbers)

        record = result.single()

        if record is None:
            return 0

        return record["deleted"]


def cleanup_stale_relationships(tx, relationships):
    relationship_keys = []

    for relationship in relationships:
        source = relationship[0]
        target = relationship[1]
        relationship_type = relationship[2]

        relationship_keys.append(
            source + "||" + relationship_type.upper() + "||" + target
        )

    query = """
        MATCH (source:Standard)-[r]->(target:Standard)
        WHERE type(r) <> 'HAS_VERSION'
        WITH source, r, target,
             source.standard_number AS source_number,
             target.standard_number AS target_number,
             type(r) AS relationship_type
        WITH source, r, target,
             source_number + '||' +
             relationship_type + '||' +
             target_number AS relationship_key
        WHERE NOT relationship_key IN $relationships
        DELETE r
        RETURN count(r) AS deleted
    """

    if _is_session_like(tx):
        result = tx.run(query, relationships=relationship_keys)

        record = result.single()

        if record is None:
            return 0

        try:
            return record["deleted"]
        except (KeyError, IndexError, TypeError):
            return 0

    with tx.session() as session:
        result = session.run(query, relationships=relationship_keys)

        record = result.single()

        if record is None:
            return 0

        return record["deleted"]


def remove_managed_relationships(driver):
    query = """
        MATCH (source:Standard)-[r]->(target:Standard)
        WHERE type(r) <> 'HAS_VERSION'
        DELETE r
        RETURN count(r) AS deleted
    """

    with driver.session() as session:
        result = session.run(query)

        record = result.single()

        if record is None:
            return 0

        return record["deleted"]


def sync_standard(tx, standard):
    query = """
        MERGE (s:Standard {
            standard_number: $standard_number
        })
        SET
            s.title = $title,
            s.description = $description,
            s.status = $status
    """

    parameters = {
        "standard_number": standard.standard_number,
        "title": standard.title,
        "description": standard.description,
        "status": standard.status,
    }

    if hasattr(standard, "id"):
        parameters["postgres_id"] = standard.id

    if _is_session_like(tx):
        tx.run(query, **parameters)
        return

    with tx.session() as session:
        session.run(query, **parameters)


def sync_version(tx, version, standard_number=None):
    if isinstance(version, str):
        actual_standard_number = version
        actual_version = standard_number

        version_number = actual_version.version_number

        effective_date = (
            actual_version.effective_date.isoformat()
            if actual_version.effective_date
            else None
        )

        status = actual_version.status
        document_path = getattr(actual_version, "document_path", None)

        postgres_id = getattr(actual_version, "id", None)

    else:
        actual_standard_number = standard_number

        version_number = version.version_number

        effective_date = (
            version.effective_date.isoformat() if version.effective_date else None
        )

        status = version.status

        document_path = getattr(version, "document_path", None)

        postgres_id = getattr(version, "id", None)

    query = """
        MERGE (s:Standard {
            standard_number: $standard_number
        })

        MERGE (v:StandardVersion {
            standard_number: $standard_number,
            version_number: $version_number
        })

        SET
            v.effective_date = $effective_date,
            v.status = $status,
            v.document_path = $document_path,
            v.postgres_id = $postgres_id

        MERGE (s)-[:HAS_VERSION]->(v)
    """

    parameters = {
        "standard_number": actual_standard_number,
        "version_number": version_number,
        "effective_date": effective_date,
        "status": status,
        "document_path": document_path,
        "postgres_id": postgres_id,
    }

    if _is_session_like(tx):
        tx.run(query, **parameters)
        return

    with tx.session() as session:
        session.run(query, **parameters)


def sync_relationship(tx, source_standard, target_standard, relationship_type):
    safe_relationship_type = "".join(
        character if character.isalnum() or character == "_" else "_"
        for character in relationship_type.upper()
    )

    query = f"""
        MATCH (source:Standard {{
            standard_number: $source_standard
        }})

        MATCH (target:Standard {{
            standard_number: $target_standard
        }})

        MERGE (source)-[r:`{safe_relationship_type}`]->(target)

        SET r.verified = true
    """

    parameters = {
        "source_standard": source_standard,
        "target_standard": target_standard,
    }

    if _is_session_like(tx):
        tx.run(query, **parameters)
        return

    with tx.session() as session:
        session.run(query, **parameters)


def sync_relationship_model(tx, relationship, source_standard, target_standard):
    relationship_type = relationship.relationship_type

    if not relationship_type:
        return False

    safe_relationship_type = "".join(
        character if character.isalnum() or character == "_" else "_"
        for character in relationship_type.upper()
    )

    query = f"""
        MATCH (source:Standard {{
            standard_number: $source_standard
        }})

        MATCH (target:Standard {{
            standard_number: $target_standard
        }})

        MERGE (source)-[r:`{safe_relationship_type}`]->(target)

        SET
            r.postgres_id = $postgres_id,
            r.verified = $verified
    """

    parameters = {
        "source_standard": source_standard.standard_number,
        "target_standard": target_standard.standard_number,
        "postgres_id": relationship.id,
        "verified": relationship.verified,
    }

    if _is_session_like(tx):
        tx.run(query, **parameters)
    else:
        with tx.session() as session:
            session.run(query, **parameters)

    return True


def get_postgres_relationships(db):
    relationships = (
        db.query(StandardRelationship)
        .filter(StandardRelationship.verified == True)
        .all()
    )

    postgres_relationships = []

    for relationship in relationships:
        source_standard = (
            db.query(Standard)
            .filter(Standard.id == relationship.source_standard_id)
            .first()
        )

        target_standard = (
            db.query(Standard)
            .filter(Standard.id == relationship.target_standard_id)
            .first()
        )

        if not source_standard or not target_standard:
            continue

        postgres_relationships.append(
            (
                source_standard.standard_number,
                target_standard.standard_number,
                relationship.relationship_type,
            )
        )

    return relationships, postgres_relationships


def sync_database():
    db = SessionLocal()
    driver = get_driver()

    try:
        standards = db.query(Standard).all()

        standard_numbers = [standard.standard_number for standard in standards]

        removed_standards = cleanup_removed_standards(driver, standard_numbers)

        print(f"Removed stale standards: {removed_standards}")

        with driver.session() as session:
            for standard in standards:
                sync_standard(session, standard)

                versions = (
                    db.query(StandardVersion)
                    .filter(StandardVersion.standard_id == standard.id)
                    .all()
                )

                for version in versions:
                    sync_version(session, version, standard.standard_number)

        print(f"Standards synchronized: {len(standards)}")

        relationships, postgres_relationships = get_postgres_relationships(db)

        removed_relationships = cleanup_stale_relationships(
            driver, postgres_relationships
        )

        print(f"Removed stale relationships: {removed_relationships}")

        synced_relationships = 0

        with driver.session() as session:
            for relationship in relationships:
                source_standard = (
                    db.query(Standard)
                    .filter(Standard.id == relationship.source_standard_id)
                    .first()
                )

                target_standard = (
                    db.query(Standard)
                    .filter(Standard.id == relationship.target_standard_id)
                    .first()
                )

                if not source_standard or not target_standard:
                    continue

                synced = sync_relationship_model(
                    session, relationship, source_standard, target_standard
                )

                if synced:
                    synced_relationships += 1

        print(f"Verified relationships synchronized: {synced_relationships}")

        return True

    finally:
        driver.close()
        db.close()


def main():
    result = sync_database()

    if result:
        print("Neo4j synchronization completed.")


if __name__ == "__main__":
    main()