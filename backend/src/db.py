from sqlmodel import Session
from contextlib import contextmanager
import os
from sqlmodel import create_engine

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)

@contextmanager
def get_session():
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
