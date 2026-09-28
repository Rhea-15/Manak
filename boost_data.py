from src.backend.database import SessionLocal
from src.db_graph.models import Standard, StandardVersion, QCORequirement, DataSource
from datetime import date

db = SessionLocal()
std = db.query(Standard).filter_by(standard_number="IS 456").first()

if std:
    # 1. Add an authoritative source
    src = DataSource(source_name="BIS Official Portal", source_type="GOVERNMENT", is_authoritative=True)
    db.add(src)
    db.commit()
    db.refresh(src)
    
    # 2. Add an Active Version (Boosts score by +60%)
    ver = StandardVersion(
        standard_id=std.id, source_id=src.id, version_number="2000", 
        effective_date=date(2000, 1, 1), status="active"
    )
    db.add(ver)
    
    # 3. Add a Verified QCO Requirement (Boosts score by +25% and triggers "Compliant" tag)
    qco = QCORequirement(
        standard_id=std.id, source_id=src.id, qco_reference="Mandatory QCO 2024", 
        verified=True, is_active=True
    )
    db.add(qco)
    
    db.commit()
    print("IS 456 Compliance Data Boosted Successfully!")
else:
    print("IS 456 not found. Make sure you ran seed_relations.py!")