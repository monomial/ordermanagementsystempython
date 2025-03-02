from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import and_

from app.db.database import get_db
from app.models.models import Order, Customer, Product, Inventory, order_products
from app.schemas.schemas import OrderCreate, Order as OrderSchema, OrderUpdate, OrderItem

router = APIRouter()

@router.post("/", response_model=OrderSchema, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Check if customer exists
    customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Create new order
    db_order = Order(
        customer_id=order.customer_id,
        status=order.status
    )
    db.add(db_order)
    db.flush()  # Flush to get the order ID
    
    total_amount = 0.0
    
    # Add order items
    for item in order.items:
        # Check if product exists
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item.product_id} not found"
            )
        
        # Check inventory
        inventory = db.query(Inventory).filter(Inventory.product_id == item.product_id).first()
        if not inventory or inventory.quantity < item.quantity:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough inventory for product with ID {item.product_id}"
            )
        
        # Update inventory
        inventory.quantity -= item.quantity
        
        # Add product to order with quantity and price
        stmt = order_products.insert().values(
            order_id=db_order.id,
            product_id=product.id,
            quantity=item.quantity,
            unit_price=product.price
        )
        db.execute(stmt)
        
        # Update total amount
        total_amount += product.price * item.quantity
    
    # Update order total
    db_order.total_amount = total_amount
    
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/", response_model=List[OrderSchema])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orders = db.query(Order).offset(skip).limit(limit).all()
    return orders

@router.get("/{order_id}", response_model=OrderSchema)
def read_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return db_order

@router.put("/{order_id}", response_model=OrderSchema)
def update_order(order_id: int, order: OrderUpdate, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Update order fields
    update_data = order.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)
    
    db.commit()
    db.refresh(db_order)
    return db_order

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Get order items to restore inventory
    order_items = db.query(order_products).filter(order_products.c.order_id == order_id).all()
    
    # Restore inventory for each product
    for item in order_items:
        inventory = db.query(Inventory).filter(Inventory.product_id == item.product_id).first()
        if inventory:
            inventory.quantity += item.quantity
    
    # Delete order (cascade will delete order items)
    db.delete(db_order)
    db.commit()
    return None

@router.get("/{order_id}/items", response_model=List[OrderItem])
def read_order_items(order_id: int, db: Session = Depends(get_db)):
    # Check if order exists
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Get order items with product information
    items = []
    order_items = db.query(order_products).filter(order_products.c.order_id == order_id).all()
    
    for item in order_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            items.append({
                "product_id": product.id,
                "product_name": product.name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "subtotal": item.quantity * item.unit_price
            })
    
    return items 