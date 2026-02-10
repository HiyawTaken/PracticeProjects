from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Define the DB location
SQLALCHEMY_DATABASE_URL = "sqlite:///./users_example.db"

# 2. Create the Engine (The actual connection)
# check_same_thread=False is required ONLY for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Create a Session Factory (Produces new sessions on demand)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Create the Base Class (All models inherit from this)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()