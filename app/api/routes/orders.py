from fastapi import APIRouter, HTTPException, status
from typing import List
from tortoise import transactions

from app.models.models import Order, Customer, Product, Inventory, OrderItem
from app.schemas.schemas import OrderCreate, Order as OrderSchema, OrderUpdate, OrderItem as OrderItemSchema

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
            item_subtotal = product.price * item.quantity
            await OrderItem.create(
                order=db_order,
                product=product,
                quantity=item.quantity,
                unit_price=product.price,
                subtotal=item_subtotal
            )
            
            # Update total amount
            total_amount += product.price * item.quantity
        
        # Update order total
        db_order.total_amount = total_amount
        await db_order.save()
    
    # Fetch the created order with all related data
    created_order = await Order.filter(id=db_order.id).prefetch_related('customer', 'items__product').first()
    
    # Format the order with customer data
    order_dict = {
        "id": created_order.id,
        "customer_id": created_order.customer.id,
        "status": created_order.status,
        "order_date": created_order.order_date,
        "total_amount": created_order.total_amount,
        "created_at": created_order.created_at,
        "updated_at": created_order.updated_at,
        "customer": created_order.customer,
        "items": []
    }
    
    # Add order items
    for item in created_order.items:
        order_dict["items"].append({
            "product_id": item.product.id,
            "product_name": item.product.name,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "subtotal": item.subtotal
        })
    
    return order_dict

@router.get("/", response_model=List[OrderSchema])
async def read_orders(skip: int = 0, limit: int = 100):
    # Use prefetch_related to load the customer and items in a single query
    orders = await Order.all().prefetch_related('customer', 'items__product').offset(skip).limit(limit)
    
    # Process each order to properly format the response
    result = []
    for order in orders:
        # Format the order with customer data
        order_dict = {
            "id": order.id,
            "customer_id": order.customer.id,
            "status": order.status,
            "order_date": order.order_date,
            "total_amount": order.total_amount,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "customer": order.customer,
            "items": []
        }
        
        # Add order items
        for item in order.items:
            order_dict["items"].append({
                "product_id": item.product.id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "subtotal": item.subtotal
            })
        
        result.append(order_dict)
    
    return result

@router.get("/{order_id}", response_model=OrderSchema)
async def read_order(order_id: int):
    # Get order with prefetched relations
    db_order = await Order.filter(id=order_id).prefetch_related('customer', 'items__product').first()
    if db_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Format the order with customer data
    order_dict = {
        "id": db_order.id,
        "customer_id": db_order.customer.id,
        "status": db_order.status,
        "order_date": db_order.order_date,
        "total_amount": db_order.total_amount,
        "created_at": db_order.created_at,
        "updated_at": db_order.updated_at,
        "customer": db_order.customer,
        "items": []
    }
    
    # Add order items
    for item in db_order.items:
        order_dict["items"].append({
            "product_id": item.product.id,
            "product_name": item.product.name,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "subtotal": item.subtotal
        })
    
    return order_dict

@router.put("/{order_id}", response_model=OrderSchema)
async def update_order(order_id: int, order: OrderUpdate):
    db_order = await Order.filter(id=order_id).first()
    if db_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Update order fields
    update_data = order.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)
    
    await db_order.save()
    
    # Fetch the updated order with all related data
    updated_order = await Order.filter(id=order_id).prefetch_related('customer', 'items__product').first()
    
    # Format the order with customer data
    order_dict = {
        "id": updated_order.id,
        "customer_id": updated_order.customer.id,
        "status": updated_order.status,
        "order_date": updated_order.order_date,
        "total_amount": updated_order.total_amount,
        "created_at": updated_order.created_at,
        "updated_at": updated_order.updated_at,
        "customer": updated_order.customer,
        "items": []
    }
    
    # Add order items
    for item in updated_order.items:
        order_dict["items"].append({
            "product_id": item.product.id,
            "product_name": item.product.name,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "subtotal": item.subtotal
        })
    
    return order_dict

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int):
    db_order = await Order.filter(id=order_id).prefetch_related('items__product').first()
    if db_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    async with transactions.in_transaction():
        # Restore inventory for each product
        for item in db_order.items:
            if item.quantity > 0:
                inventory = await Inventory.filter(product_id=item.product.id).first()
                if inventory:
                    inventory.quantity += item.quantity
                    await inventory.save()
        
        # Delete the order (this will also delete related order items due to cascade)
        await db_order.delete()
    
    return None

@router.get("/{order_id}/items", response_model=List[OrderItemSchema])
async def read_order_items(order_id: int):
    # Check if order exists
    order = await Order.filter(id=order_id).prefetch_related('items__product').first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Get order items with product information
    items = []
    for item in order.items:
        items.append({
            "product_id": item.product.id,
            "product_name": item.product.name,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "subtotal": item.subtotal
        })
    
    return items

@router.get("/debug/inventory", status_code=status.HTTP_200_OK)
async def debug_inventory():
    """Debug endpoint to check inventory levels for all products"""
    inventory_data = []
    
    # Get all products with their inventory
    products = await Product.all().prefetch_related("inventory")
    
    for product in products:
        inventory_level = 0
        if hasattr(product, "inventory") and product.inventory:
            inventory_level = product.inventory.quantity
            
        inventory_data.append({
            "product_id": product.id,
            "product_name": product.name,
            "inventory_level": inventory_level
        })
    
    return inventory_data 