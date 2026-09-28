from sqlalchemy import text
from src.backend.database import engine

def init_db():
    """Initialize database schema and seed initial data synchronously"""
    with engine.begin() as conn:
        # Create version tracking table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS standards_versions (
                id SERIAL PRIMARY KEY,
                standard_code VARCHAR(50) NOT NULL UNIQUE,
                title VARCHAR(255) NOT NULL,
                version VARCHAR(20) NOT NULL,
                publication_year INT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create QCO/ISI marks table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS certification_marks (
                id SERIAL PRIMARY KEY,
                standard_id INT REFERENCES standards_versions(id),
                mark_type VARCHAR(50) NOT NULL,
                description TEXT,
                is_mandatory BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create audit logs table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(100),
                action VARCHAR(100) NOT NULL,
                resource_type VARCHAR(50),
                resource_id VARCHAR(100),
                old_value JSONB,
                new_value JSONB,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(50)
            );
        """))
        
    print("✓ Database schema initialized")

if __name__ == "__main__":
    init_db()