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
    name: str | None = None
    city: str | None = None
    industry: str | None = None
    cargo_type: str | None = None
    size: CustomerSize | None = None


class CustomerSchema(CustomerBase):
    id: int

    class Config:
        from_attributes = True 