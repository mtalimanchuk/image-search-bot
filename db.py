from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DB_CONNECTION, DB_ECHO


engine = create_engine(DB_CONNECTION, echo=DB_ECHO)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    rating = Column(Integer, default=0)

class Picture(Base):
    __tablename__ = "pictures"

    id = Column(Integer, primary_key=True)
    message_link = Column(String)
    path = Column(String)
    rating = Column(Integer, default=0)


Base.metadata.create_all(engine)
