import asyncio
import os
import sys
import random

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tortoise import Tortoise
from app.models.models import Order, Product, OrderItem

# Get the absolute path to the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SQLite database URL with absolute path
SQLALCHEMY_DATABASE_URL = f"sqlite://{os.path.join(BASE_DIR, 'order_management.db')}"

async def add_sample_order_items():
    print("Starting to add sample order items...")
    
    # Initialize Tortoise ORM
    await Tortoise.init(
        db_url=SQLALCHEMY_DATABASE_URL,
        modules={"models": ["app.models.models"]}
    )
    
    # Get all orders and products
    orders = await Order.all()
    products = await Product.all()
    
    # For each order, add 1-3 random products as order items
    for order in orders:
        # Randomly select 1-3 products for this order
        num_products = random.randint(1, 3)
        selected_products = random.sample(list(products), min(num_products, len(products)))
        
        order_total = 0.0
        
        for product in selected_products:
            # Random quantity between 1 and 5
            quantity = random.randint(1, 5)
            unit_price = product.price
            subtotal = unit_price * quantity
            
            # Create the order item
            await OrderItem.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=subtotal
            )
            
            order_total += subtotal
            
            print(f"Added {quantity} x {product.name} to Order #{order.id}")
        
        # Update the order's total amount
        order.total_amount = order_total
        await order.save()
        print(f"Updated Order #{order.id} total amount to ${order_total:.2f}")
    
    # Close connections
    await Tortoise.close_connections()
    
    print("Sample order items added successfully!")

if __name__ == "__main__":
    asyncio.run(add_sample_order_items()) 