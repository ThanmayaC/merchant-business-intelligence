"""
database.py — the connection between Python and PostgreSQL.

ANALOGY:
  - ENGINE  = the telephone line to the database (created once, reused).
  - SESSION = one phone call. You open it, ask questions / save data,
              then hang up. Each HTTP request gets its own call.
  - BASE    = the "parent class" every table class inherits from, so
              SQLAlchemy knows "this Python class is a database table".

CONCEPT — SQLAlchemy & ORM:
  SQLAlchemy is a Python toolkit for talking to SQL databases.
  ORM (Object-Relational Mapper) means: a database TABLE becomes a Python
  CLASS, and a ROW becomes a Python OBJECT. You write
      db.query(Merchant).all()
  instead of
      SELECT * FROM merchants;
  Mongoose does the same job for MongoDB.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config.settings import settings

# The engine keeps a "pool" of open connections so each request is fast.
# pool_pre_ping=True checks a connection is still alive before using it.
engine = create_engine(settings.database_url, pool_pre_ping=True)

# A factory that creates new Session objects (new "phone calls").
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Every ORM model (table) will inherit from this class."""


def get_db():
    """
    FastAPI "dependency" that gives a route one database session.

    `yield` hands the session to the route. When the route finishes
    (even with an error), the code after `yield` runs and closes it.
    Like borrowing a library book: you always return it at the end.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
