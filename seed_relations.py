from src.backend.database import SessionLocal
from src.db_graph.models import Standard, StandardRelationship
from src.db_graph.sync_neo4j import sync_database

db = SessionLocal()

# 1. Ensure the standards we want to link exist in the DB
standards_to_ensure = [
    ("IS 456", "Plain and Reinforced Concrete", "active"),
    ("IS 10262", "Concrete Mix Proportioning", "active"),
    ("IS 383", "Coarse and Fine Aggregates", "active"),
    ("IS 8112", "43 Grade Ordinary Portland Cement", "active")
]

for std_num, title, status in standards_to_ensure:
    if not db.query(Standard).filter_by(standard_number=std_num).first():
        db.add(Standard(standard_number=std_num, title=title, status=status))
db.commit()

# 2. Fetch their IDs
std_map = {s.standard_number: s.id for s in db.query(Standard).all()}

# 3. Define the hierarchical relationships
relations = [
    ("IS 456", "IS 10262", "NORMATIVE_REFERENCE"),
    ("IS 456", "IS 383", "NORMATIVE_REFERENCE"),
    ("IS 10262", "IS 8112", "NORMATIVE_REFERENCE"),
]

# 4. Insert into PostgreSQL
for source, target, rel_type in relations:
    src_id, tgt_id = std_map.get(source), std_map.get(target)
    if src_id and tgt_id:
        exists = db.query(StandardRelationship).filter_by(
            source_standard_id=src_id, target_standard_id=tgt_id
        ).first()
        if not exists:
            db.add(StandardRelationship(
                source_standard_id=src_id, 
                target_standard_id=tgt_id, 
                relationship_type=rel_type, 
                verified=True
            ))
db.commit()
print("Relationships seeded in PostgreSQL!")

# 5. Push changes to Neo4j
sync_database()
print("Neo4j sync complete! Refresh your Neo4j Browser.")