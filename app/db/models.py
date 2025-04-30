from sqlalchemy import Column, Enum, Integer, String

from app.config.options import CustomerSize
from app.db.database import Base


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    city = Column(String)
    industry = Column(String)
    cargo_type = Column(String)
    size = Column(Enum(CustomerSize))
