from fastapi import APIRouter, HTTPException, status
from typing import List
from tortoise import transactions

from app.models.models import Order, Customer, Product, Inventory
from app.schemas.schemas import OrderCreate, Order as OrderSchema, OrderUpdate, OrderItem

router = APIRouter()

@router.post("/", response_model=OrderSchema, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate):
    # Check if customer exists
    customer = await Customer.filter(id=order.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    async with transactions.in_transaction():
        # Create new order
        db_order = await Order.create(customer=customer, status=order.status)
        
        total_amount = 0.0
        
        # Add order items
        for item in order.items:
            # Check if product exists
            product = await Product.filter(id=item.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {item.product_id} not found"
                )
            
            # Check inventory
            inventory = await Inventory.filter(product_id=item.product_id).first()
            if not inventory or inventory.quantity < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Not enough inventory for product with ID {item.product_id}"
                )
            
            # Update inventory
            inventory.quantity -= item.quantity
            await inventory.save()
            
            # Add product to order with quantity and price
            await db_order.products.add(product, through={"quantity": item.quantity, "unit_price": product.price})
            
            # Update total amount
            total_amount += product.price * item.quantity
        
        # Update order total
        db_order.total_amount = total_amount
        await db_order.save()
    
    return db_order

@router.get("/", response_model=List[OrderSchema])
async def read_orders(skip: int = 0, limit: int = 100):
    orders = await Order.all().offset(skip).limit(limit)
    return orders

@router.get("/{order_id}", response_model=OrderSchema)
async def read_order(order_id: int):
    db_order = await Order.filter(id=order_id).first()
    if db_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return db_order

@router.put("/{order_id}", response_model=OrderSchema)
async def update_order(order_id: int, order: OrderUpdate):
    db_order = await Order.filter(id=order_id).first()
    if db_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Update order fields
    update_data = order.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)
    
    await db_order.save()
    return db_order

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int):
    db_order = await Order.filter(id=order_id).first()
    if db_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Get order items to restore inventory
    order_items = await db_order.products.all()
    
    # Restore inventory for each product
    for item in order_items:
        inventory = await Inventory.filter(product_id=item.id).first()
        if inventory:
            inventory.quantity += item.quantity
            await inventory.save()
    
    await db_order.delete()
    return None

@router.get("/{order_id}/items", response_model=List[OrderItem])
async def read_order_items(order_id: int):
    # Check if order exists
    order = await Order.filter(id=order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Get order items with product information
    items = []
    order_items = await order.products.all()
    
    for item in order_items:
        items.append({
            "product_id": item.id,
            "product_name": item.name,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "subtotal": item.quantity * item.unit_price
        })
    
    return items 