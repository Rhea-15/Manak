import os
from datetime import date
from src.backend.cache import get_redis_client
from src.backend.database import SessionLocal
from src.db_graph.models import Standard, StandardRelationship, StandardVersion, QCORequirement, DataSource
from src.db_graph.sync_neo4j import sync_database

def nuke_and_rebuild():
    print("1. Flushing Redis Cache...")
    try:
        get_redis_client().flushall()
        print("   -> Redis wiped clean!")
    except Exception as e:
        print(f"   -> Warning: Could not flush Redis ({e}).")

    print("2. Setting up perfect PostgreSQL data...")
    db = SessionLocal()
    
    # Ensure base standards exist
    standards = {
        "IS 456": "Plain and Reinforced Concrete",
        "IS 10262": "Concrete Mix Proportioning",
        "IS 383": "Coarse and Fine Aggregates"
    }
    for num, title in standards.items():
        if not db.query(Standard).filter_by(standard_number=num).first():
            db.add(Standard(standard_number=num, title=title, status="active"))
    db.commit()
    
    std_456 = db.query(Standard).filter_by(standard_number="IS 456").first()
    std_10262 = db.query(Standard).filter_by(standard_number="IS 10262").first()
    std_383 = db.query(Standard).filter_by(standard_number="IS 383").first()
    
    # Setup authoritative source
    src = db.query(DataSource).filter_by(source_name="BIS Official Portal").first()
    if not src:
        src = DataSource(source_name="BIS Official Portal", source_type="GOVERNMENT", is_authoritative=True)
        db.add(src)
        db.commit()
        
    # Clean old IS 456 data to avoid duplicate errors
    db.query(QCORequirement).filter_by(standard_id=std_456.id).delete()
    db.query(StandardVersion).filter_by(standard_id=std_456.id).delete()
    
    # Add compliance data (This fixes the 0% score and "Needs Verification" tag!)
    db.add(StandardVersion(standard_id=std_456.id, source_id=src.id, version_number="2000", effective_date=date(2000, 1, 1), status="active"))
    db.add(QCORequirement(standard_id=std_456.id, source_id=src.id, qco_reference="Mandatory QCO 2024", verified=True, is_active=True))
    
    # Setup Relationships for the Graph
    for tgt in [std_10262, std_383]:
        if not db.query(StandardRelationship).filter_by(source_standard_id=std_456.id, target_standard_id=tgt.id).first():
            db.add(StandardRelationship(source_standard_id=std_456.id, target_standard_id=tgt.id, relationship_type="NORMATIVE_REFERENCE", verified=True))
            
    db.commit()
    db.close()
    print("   -> PostgreSQL perfectly seeded!")
    
    print("3. Pushing data to Neo4j...")
    sync_database()
    print("   -> Neo4j Graph synced!")
    print("\nSUCCESS! All systems go.")

if __name__ == "__main__":
    nuke_and_rebuild()