﻿from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine, SQLModel, Session
from app.config import settings

engine = create_engine(settings.database_url, echo=False)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)

def get_session() -> Session:
    with Session(engine) as session:
        yield session
