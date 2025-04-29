from typing import Optional
from pydantic import BaseModel
from app.config.options import CustomerSize


class CustomerBase(BaseModel):
    name: str
    city: str
    industry: str
    cargo_type: str
    size: CustomerSize


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    industry: Optional[str] = None
    cargo_type: Optional[str] = None
    size: Optional[CustomerSize] = None


class CustomerSchema(CustomerBase):
    id: int

    class Config:
        from_attributes = True
