from fastapi import APIRouter, HTTPException, status
from typing import List

from app.models.models import Customer
from app.schemas.schemas import CustomerCreate, Customer as CustomerSchema, CustomerUpdate

router = APIRouter()

@router.post("/", response_model=CustomerSchema, status_code=status.HTTP_201_CREATED)
async def create_customer(customer: CustomerCreate):
    # Check if customer with email already exists
    db_customer = await Customer.filter(email=customer.email).first()
    if db_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new customer
    db_customer = await Customer.create(**customer.dict())
    return db_customer

@router.get("/", response_model=List[CustomerSchema])
async def read_customers(skip: int = 0, limit: int = 100):
    customers = await Customer.all().offset(skip).limit(limit)
    return customers

@router.get("/{customer_id}", response_model=CustomerSchema)
async def read_customer(customer_id: int):
    db_customer = await Customer.filter(id=customer_id).first()
    if db_customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return db_customer

@router.put("/{customer_id}", response_model=CustomerSchema)
async def update_customer(customer_id: int, customer: CustomerUpdate):
    db_customer = await Customer.filter(id=customer_id).first()
    if db_customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Update customer fields
    update_data = customer.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_customer, key, value)
    
    await db_customer.save()
    return db_customer

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(customer_id: int):
    db_customer = await Customer.filter(id=customer_id).first()
    if db_customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    await db_customer.delete()
    return None 