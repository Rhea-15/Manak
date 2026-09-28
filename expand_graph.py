from src.backend.database import SessionLocal
from src.db_graph.models import Standard, StandardRelationship
from src.db_graph.sync_neo4j import sync_database

def expand_graph():
    db = SessionLocal()
    
    # 1. Add supporting standard definitions
    supporting_standards = {
        "IS 9103": "Concrete Admixtures",
        "IS 2386": "Tests for Aggregates",
        "IS 456": "Plain and Reinforced Concrete",
        "IS 383": "Coarse and Fine Aggregates"
    }
    
    for num, title in supporting_standards.items():
        if not db.query(Standard).filter_by(standard_number=num).first():
            db.add(Standard(standard_number=num, title=title, status="active"))
    db.commit()

    # 2. Get the root standard (IS 10262)
    std_10262 = db.query(Standard).filter_by(standard_number="IS 10262").first()
    
    if not std_10262:
        print("Error: IS 10262 not found in database.")
        return

    # 3. Create multiple relationships linking outward from IS 10262
    targets = ["IS 9103", "IS 2386", "IS 456", "IS 383"]
    
    for target_num in targets:
        tgt_std = db.query(Standard).filter_by(standard_number=target_num).first()
        if tgt_std:
            # Check if relationship already exists to avoid duplicates
            exists = db.query(StandardRelationship).filter_by(
                source_standard_id=std_10262.id, 
                target_standard_id=tgt_std.id
            ).first()
            
            if not exists:
                db.add(StandardRelationship(
                    source_standard_id=std_10262.id,
                    target_standard_id=tgt_std.id,
                    relationship_type="NORMATIVE_REFERENCE",
                    verified=True
                ))
    
    db.commit()
    db.close()
    
    print("PostgreSQL relationships added!")
    
    # 4. Sync the new complex web to Neo4j
    sync_database()
    print("Neo4j Graph expanded successfully!")

if __name__ == "__main__":
    expand_graph()