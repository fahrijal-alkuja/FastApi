from config.db import Base, engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine, checkfirst=True)


def get_db() -> Session:
    db = Session(bind=engine)
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    finally:
        db.close()
