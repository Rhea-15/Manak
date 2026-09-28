from src.backend.database import SessionLocal
from src.db_graph.models import Standard, StandardVersion, QCORequirement, DataSource
from datetime import date

db = SessionLocal()
std = db.query(Standard).filter_by(standard_number="IS 10262").first()

if std:
    src = db.query(DataSource).filter_by(source_name="BIS Official Portal").first()
    if not src:
        src = DataSource(source_name="BIS Official Portal", source_type="GOVERNMENT", is_authoritative=True)
        db.add(src)
        db.commit()
        
    # Clean old IS 10262 data
    db.query(QCORequirement).filter_by(standard_id=std.id).delete()
    db.query(StandardVersion).filter_by(standard_id=std.id).delete()
    
    # Add an Active Version (Gives 35 points + 25 points = 60%)
    db.add(StandardVersion(standard_id=std.id, source_id=src.id, version_number="2019", effective_date=date(2019, 1, 1), status="active"))
    
    # Add an UNVERIFIED QCO Requirement (Misses the remaining 40 points & triggers a Warning)
    db.add(QCORequirement(standard_id=std.id, source_id=src.id, qco_reference="Mandatory QCO 2024", verified=False, is_active=True))
    
    db.commit()
    print("IS 10262 Partial Compliance Data Added (Target Score: 60%)!")