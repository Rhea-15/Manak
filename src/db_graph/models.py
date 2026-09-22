from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)

from src.backend.database import Base


class Standard(Base):
    __tablename__ = "standards"

    id = Column(Integer, primary_key=True)
    standard_number = Column(String(100), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class StandardVersion(Base):
    __tablename__ = "standard_versions"

    id = Column(Integer, primary_key=True)
    standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False)
    version_number = Column(String(50), nullable=False)
    effective_date = Column(Date, nullable=True)
    status = Column(String(50), nullable=False)
    document_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Amendment(Base):
    __tablename__ = "amendments"

    id = Column(Integer, primary_key=True)
    standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False)
    amendment_number = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    amendment_date = Column(Date, nullable=True)
    document_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CertificationRule(Base):
    __tablename__ = "certification_rules"

    id = Column(Integer, primary_key=True)
    standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False)
    rule_type = Column(String(100), nullable=False)
    rule_name = Column(String(255), nullable=False)
    rule_description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), nullable=True)
    endpoint = Column(String(255), nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ReviewQueue(Base):
    __tablename__ = "review_queue"

    id = Column(Integer, primary_key=True)
    document_name = Column(String(255), nullable=False)
    document_path = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False)
    submitted_by = Column(String(100), nullable=True)
    reviewed_by = Column(String(100), nullable=True)
    review_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True)
    source_name = Column(String(255), nullable=False)
    source_type = Column(String(100), nullable=False)
    source_url = Column(String(1000), nullable=True)
    document_reference = Column(String(255), nullable=True)
    retrieved_at = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(String(100), nullable=True)
    source_hash = Column(String(128), nullable=True)
    is_authoritative = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class QCORequirement(Base):
    __tablename__ = "qco_requirements"

    id = Column(Integer, primary_key=True)
    standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False)
    qco_reference = Column(String(300), nullable=True)
    requirement_text = Column(Text, nullable=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=True)
    effective_from = Column(Date, nullable=True)
    effective_to = Column(Date, nullable=True)
    verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ISIRequirement(Base):
    __tablename__ = "isi_requirements"

    id = Column(Integer, primary_key=True)
    standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False)
    requirement_name = Column(String(300), nullable=True)
    requirement_text = Column(Text, nullable=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=True)
    effective_from = Column(Date, nullable=True)
    effective_to = Column(Date, nullable=True)
    verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class CRSRequirement(Base):
    __tablename__ = "crs_requirements"

    id = Column(Integer, primary_key=True)
    standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False)
    requirement_name = Column(String(300), nullable=True)
    requirement_text = Column(Text, nullable=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=True)
    effective_from = Column(Date, nullable=True)
    effective_to = Column(Date, nullable=True)
    verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class HallmarkingRequirement(Base):
    __tablename__ = "hallmarking_requirements"

    id = Column(Integer, primary_key=True)
    standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False)
    requirement_name = Column(String(300), nullable=True)
    requirement_text = Column(Text, nullable=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=True)
    effective_from = Column(Date, nullable=True)
    effective_to = Column(Date, nullable=True)
    verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class StandardRelationship(Base):
    __tablename__ = "standard_relationships"

    id = Column(Integer, primary_key=True)
    source_standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False)
    target_standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False)
    relationship_type = Column(String(100), nullable=False)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=True)
    verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            "source_standard_id",
            "target_standard_id",
            "relationship_type",
            name="uq_standard_relationship",
        ),
        Index("ix_standard_relationship_source", "source_standard_id"),
        Index("ix_standard_relationship_target", "target_standard_id"),
        Index("ix_standard_relationship_verified", "verified"),
    )
