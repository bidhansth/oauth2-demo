from app.database import engine, Base
from app.config import settings

def init_db():
    from app.models import User, OAuthIdentity
    
    print(f"Initializing database at: {settings.DATABASE_URL}")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

def drop_all_tables():
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped")

if __name__ == "__main__":
    init_db()