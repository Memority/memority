from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from settings import settings

engine = create_engine(f'sqlite:///{settings.db_path}')
Session = sessionmaker(bind=engine)

Base = declarative_base()

session = Session()


def create_tables():
    return Base.metadata.create_all(engine)
