from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import declarative_base
from app.config.options import CustomerSize

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    city = Column(String)
    industry = Column(String)
    cargo_type = Column(String)
    size = Column(Enum(CustomerSize)) 