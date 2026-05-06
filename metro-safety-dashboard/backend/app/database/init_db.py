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
