from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models import Customer
from app.schemas.customer import CustomerCreate, Customer as CustomerSchema
from app.config.options import CustomerSize
import logging
from fastapi.responses import JSONResponse
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/size-options/")
async def get_size_options():
    """获取所有可用的客户规模选项"""
    try:
        options = CustomerSize.get_options()
        return {"options": options}
    except Exception as e:
        logger.error(f"Error in get_size_options: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

@router.post("/", response_model=CustomerSchema)
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """创建新客户"""
    try:
        db_customer = Customer(**customer.model_dump())
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer
    except Exception as e:
        logger.error(f"Error creating customer: {str(e)}")
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

@router.get("/", response_model=List[CustomerSchema])
async def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取客户列表"""
    try:
        customers = db.query(Customer).offset(skip).limit(limit).all()
        return customers
    except Exception as e:
        logger.error(f"Error reading customers: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

@router.get("/{customer_id}", response_model=CustomerSchema)
async def read_customer(customer_id: int, db: Session = Depends(get_db)):
    """获取单个客户详情"""
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if customer is None:
            return JSONResponse(
                status_code=404,
                content={"detail": "Customer not found"}
            )
        return customer
    except Exception as e:
        logger.error(f"Error reading customer: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

@router.put("/{customer_id}", response_model=CustomerSchema)
async def update_customer(customer_id: int, customer: CustomerCreate, db: Session = Depends(get_db)):
    """更新客户信息"""
    try:
        db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if db_customer is None:
            return JSONResponse(
                status_code=404,
                content={"detail": "Customer not found"}
            )
        
        for key, value in customer.model_dump().items():
            setattr(db_customer, key, value)
        
        db.commit()
        db.refresh(db_customer)
        return db_customer
    except Exception as e:
        logger.error(f"Error updating customer: {str(e)}")
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

@router.delete("/{customer_id}", response_model=CustomerSchema)
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """删除客户"""
    try:
        db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if db_customer is None:
            return JSONResponse(
                status_code=404,
                content={"detail": "Customer not found"}
            )
        
        # 保存客户信息用于返回
        customer_data = {
            "id": db_customer.id,
            "name": db_customer.name,
            "city": db_customer.city,
            "industry": db_customer.industry,
            "cargo_type": db_customer.cargo_type,
            "size": db_customer.size
        }
        
        db.delete(db_customer)
        db.commit()
        return customer_data
    except Exception as e:
        logger.error(f"Error deleting customer: {str(e)}")
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        ) 