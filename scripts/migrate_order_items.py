import asyncio
import sqlite3
import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tortoise import Tortoise
from app.models.models import Order, Product, OrderItem
from app.db.database import DATABASE_URL

async def migrate_order_items():
    print("Starting migration of order items...")
    
    # Initialize Tortoise ORM
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={"models": ["app.models.models"]}
    )
    
    # Generate schemas (creates the OrderItem table)
    print("Creating OrderItem table...")
    await Tortoise.generate_schemas(safe=True)
    
    # Get database path from DATABASE_URL
    db_path = DATABASE_URL.replace("sqlite://", "")
    
    # Connect to SQLite database directly to check for existing many-to-many table
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the order_product table exists (the default M2M table created by Tortoise)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='order_product'")
    order_product_exists = cursor.fetchone() is not None
    
    if order_product_exists:
        print("Found existing order_product table, migrating data...")
        
        # Get all entries from the order_product table
        cursor.execute("SELECT order_id, product_id FROM order_product")
        order_product_entries = cursor.fetchall()
        
        # For each entry, create an OrderItem
        for order_id, product_id in order_product_entries:
            # Get the order and product
            order = await Order.get(id=order_id)
            product = await Product.get(id=product_id)
            
            # Create a new OrderItem
            await OrderItem.create(
                order=order,
                product=product,
                quantity=1,  # Default quantity
                unit_price=product.price,  # Use current product price
                subtotal=product.price  # unit_price * quantity
            )
            
            print(f"Created OrderItem for Order {order_id}, Product {product_id}")
    else:
        print("No existing order_product table found. No data to migrate.")
    
    # Close connections
    conn.close()
    await Tortoise.close_connections()
    
    print("Migration completed successfully!")

if __name__ == "__main__":
    asyncio.run(migrate_order_items()) 