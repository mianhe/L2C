import logging
from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config.options import CustomerSize
from app.db.database import get_db
from app.db.models import Customer
from app.schemas.customer import CustomerCreate, CustomerSchema, CustomerUpdate

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
        return JSONResponse(status_code=500, content={"detail": str(e)})


@router.post("/", response_model=CustomerSchema)
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """创建客户"""
    try:
        logger.info("=== Starting customer creation ===")
        logger.info(f"Received customer data: {customer.dict()}")
        logger.info("Validating customer data...")

        db_customer = Customer(**customer.dict())
        logger.info("Customer model created successfully")

        logger.info("Adding to database session...")
        db.add(db_customer)

        logger.info("Committing transaction...")
        db.commit()

        logger.info("Refreshing customer data...")
        db.refresh(db_customer)

        logger.info(f"Customer created successfully with ID: {db_customer.id}")
        return db_customer
    except Exception as e:
        logger.error("=== Error in customer creation ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error("Stack trace:", exc_info=True)
        db.rollback()
        return JSONResponse(status_code=500, content={"detail": str(e), "error_type": type(e).__name__})


@router.get("/", response_model=List[CustomerSchema])
async def list_customers(db: Session = Depends(get_db)):
    """获取客户列表"""
    try:
        logger.info("Attempting to fetch all customers")
        customers = db.query(Customer).all()
        logger.info(f"Successfully fetched {len(customers)} customers")
        for customer in customers:
            logger.debug(f"Customer data: {customer.id}, {customer.name}, {customer.size}")
        return customers
    except Exception as e:
        logger.error(f"Error listing customers: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": str(e)})


@router.get("/{customer_id}", response_model=CustomerSchema)
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """获取单个客户"""
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if customer is None:
            return JSONResponse(status_code=404, content={"detail": "Customer not found"})
        return customer
    except Exception as e:
        logger.error(f"Error getting customer: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": str(e)})


@router.put("/{customer_id}", response_model=CustomerSchema)
async def update_customer(customer_id: int, customer_update: CustomerUpdate, db: Session = Depends(get_db)):
    """更新客户"""
    try:
        db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if db_customer is None:
            return JSONResponse(status_code=404, content={"detail": "Customer not found"})

        for field, value in customer_update.dict(exclude_unset=True).items():
            setattr(db_customer, field, value)

        db.commit()
        db.refresh(db_customer)
        return db_customer
    except Exception as e:
        logger.error(f"Error updating customer: {str(e)}")
        db.rollback()
        return JSONResponse(status_code=500, content={"detail": str(e)})


@router.delete("/{customer_id}", response_model=CustomerSchema)
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """删除客户"""
    try:
        db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if db_customer is None:
            return JSONResponse(status_code=404, content={"detail": "Customer not found"})

        # 保存客户信息用于返回
        customer_data = {
            "id": db_customer.id,
            "name": db_customer.name,
            "city": db_customer.city,
            "industry": db_customer.industry,
            "cargo_type": db_customer.cargo_type,
            "size": db_customer.size,
        }

        db.delete(db_customer)
        db.commit()
        return customer_data
    except Exception as e:
        logger.error(f"Error deleting customer: {str(e)}")
        db.rollback()
        return JSONResponse(status_code=500, content={"detail": str(e)})
