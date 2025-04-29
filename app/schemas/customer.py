from pydantic import BaseModel, ConfigDict
from app.config.options import CustomerSize

class CustomerBase(BaseModel):
    name: str
    city: str
    industry: str
    cargo_type: str
    size: CustomerSize

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int

    model_config = ConfigDict(from_attributes=True) 