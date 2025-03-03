from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

# Customer schemas
class CustomerBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class CustomerInDB(CustomerBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime

class Customer(CustomerInDB):
    pass

# Product schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    sku: str

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    sku: Optional[str] = None

class ProductInDB(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime

class Product(ProductInDB):
    pass

# Inventory schemas
class InventoryBase(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=0)
    last_restock_date: Optional[datetime] = None

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=0)
    last_restock_date: Optional[datetime] = None

class InventoryInDB(InventoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime

class Inventory(InventoryInDB):
    model_config = ConfigDict(from_attributes=True)
    product: Product

# Order Item schema for order creation
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)

# Order schemas
class OrderBase(BaseModel):
    customer_id: int
    status: Optional[str] = "pending"

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[str] = None

# Order Item for response
class OrderItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float

class OrderInDB(OrderBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_date: datetime
    total_amount: float
    created_at: datetime
    updated_at: datetime

class Order(OrderInDB):
    model_config = ConfigDict(from_attributes=True)
    customer: Customer
    items: List[OrderItem] = []
    