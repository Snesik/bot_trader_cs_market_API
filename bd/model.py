from sqlalchemy import String, Column, DateTime, Float, BigInteger, ForeignKey, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import relationship
from util import config

Base = declarative_base()

bd = config['BD']
engine = create_engine(
    f"mysql+mysqlconnector://{bd['login']}:{bd['passwd']}@"
    f"{bd['host']}/{bd['bd']}")


class Items(Base):
    __tablename__ = 'items'
    id = Column(BigInteger(), primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    class_id = Column(BigInteger(), nullable=False)
    instance_id = Column(Integer(), nullable=False)
    price = relationship('Price')
    status = relationship('Status')


class Price(Base):
    __tablename__ = 'price'
    id = Column(Integer(), primary_key=True)
    buy = Column(Float())
    sell = Column(Float())
    min_price = Column(Float())
    item_id = Column(BigInteger(), ForeignKey('items.id'))


class Status(Base):
    __tablename__ = 'status'
    id = Column(Integer(), primary_key=True)
    status = Column(String(4), default='hold')
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
    item_id = Column(BigInteger(), ForeignKey('items.id'))


Base.metadata.create_all(engine)
