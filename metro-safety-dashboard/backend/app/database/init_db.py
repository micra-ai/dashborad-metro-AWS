import os
import sys
# Add parent dir to path to run script standalone
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.connection import engine, Base
from app.database.session import SessionLocal
from app.models.user import User
from app.auth.security import get_password_hash

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Check database columns, add them if missing
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    try:
        if 'epp_events' in inspector.get_table_names():
            columns = [c['name'] for c in inspector.get_columns('epp_events')]
            with engine.begin() as conn:
                if 'image_url' not in columns:
                    conn.execute(text("ALTER TABLE epp_events ADD COLUMN image_url VARCHAR;"))
                    print("Database migration: added image_url column to epp_events.")
                if 'positive_compliance_count' not in columns:
                    conn.execute(text("ALTER TABLE epp_events ADD COLUMN positive_compliance_count INTEGER DEFAULT 0;"))
                    print("Database migration: added positive_compliance_count column to epp_events.")
                if 'negative_compliance_count' not in columns:
                    conn.execute(text("ALTER TABLE epp_events ADD COLUMN negative_compliance_count INTEGER DEFAULT 0;"))
                    print("Database migration: added negative_compliance_count column to epp_events.")
    except Exception as e:
        print(f"Error migrating database: {e}")

    db = SessionLocal()
    
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        hashed_password = get_password_hash("password")
        admin = User(
            username="admin",
            email="admin@metro.cl",
            password_hash=hashed_password,
            role="admin"
        )
        db.add(admin)
        db.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")
    
    db.close()

if __name__ == "__main__":
    init_db()
