from config.db import Base, SessionLocal, engine
from sqlalchemy.exc import SQLAlchemyError

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    finally:
        db.close()
