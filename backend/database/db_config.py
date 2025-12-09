from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base 
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    """Creates all tables defined in models.py."""
    print("Initializing database tables")
    from . import models 
    Base.metadata.create_all(bind=engine)

def get_db():
    """Provides a database session for API route."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
