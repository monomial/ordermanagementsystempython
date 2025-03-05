#!/usr/bin/env python3
"""
Seed script to populate the database with initial data for Tortoise ORM.
"""
import sys
import os
from datetime import datetime, timedelta
import random
import asyncio

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tortoise import Tortoise, run_async
from app.db.database import SQLALCHEMY_DATABASE_URL
from app.models.models import Customer, Product, Order, Inventory

# Convert SQLAlchemy URL to Tortoise format
DB_URL = SQLALCHEMY_DATABASE_URL.replace('sqlite:///./','sqlite://')

async def init_tortoise():
    """Initialize Tortoise ORM."""
    await Tortoise.init(
        db_url=DB_URL,
        modules={"models": ["app.models.models"]}
    )
    await Tortoise.generate_schemas()

async def seed_database():
    """Seed the database with initial data."""
    # Initialize Tortoise ORM
    await init_tortoise()
    
    try:
        # Clear existing data - delete in reverse order of dependencies
        await Order.all().delete()
        await Inventory.all().delete()
        await Product.all().delete()
        await Customer.all().delete()
        
        # Create customers
        customers = [
            Customer(
                name="John Doe",
                email="john.doe@example.com",
                phone="555-123-4567",
                address="123 Main St, Anytown, USA",
                notes="Frequent customer, prefers email contact"
            ),
            Customer(
                name="Jane Smith",
                email="jane.smith@example.com",
                phone="555-987-6543",
                address="456 Oak Ave, Somewhere, USA",
                notes="Has corporate discount"
            ),
            Customer(
                name="Bob Johnson",
                email="bob.johnson@example.com",
                phone="555-555-5555",
                address="789 Pine Rd, Nowhere, USA",
                notes="Prefers phone contact"
            ),
            Customer(
                name="Alice Brown",
                email="alice.brown@example.com",
                phone="555-111-2222",
                address="321 Elm St, Everywhere, USA",
                notes="New customer as of Jan 2025"
            ),
            Customer(
                name="Charlie Wilson",
                email="charlie.wilson@example.com",
                phone="555-333-4444",
                address="654 Maple Dr, Anywhere, USA",
                notes="VIP customer, expedite shipping"
            )
        ]
        
        # Save customers
        saved_customers = []
        for customer in customers:
            await customer.save()
            saved_customers.append(customer)
        
        # Create products
        products = [
            Product(
                name="Laptop",
                description="High-performance laptop with 16GB RAM and 512GB SSD",
                price=1299.99,
                sku="TECH-001"
            ),
            Product(
                name="Smartphone",
                description="Latest smartphone with 128GB storage and 5G capability",
                price=899.99,
                sku="TECH-002"
            ),
            Product(
                name="Wireless Headphones",
                description="Noise-cancelling wireless headphones with 20-hour battery life",
                price=249.99,
                sku="TECH-003"
            ),
            Product(
                name="Tablet",
                description="10-inch tablet with 64GB storage and HD display",
                price=499.99,
                sku="TECH-004"
            ),
            Product(
                name="Smartwatch",
                description="Fitness tracking smartwatch with heart rate monitor",
                price=199.99,
                sku="TECH-005"
            ),
            Product(
                name="Bluetooth Speaker",
                description="Portable Bluetooth speaker with waterproof design",
                price=79.99,
                sku="TECH-006"
            ),
            Product(
                name="Wireless Mouse",
                description="Ergonomic wireless mouse with long battery life",
                price=39.99,
                sku="TECH-007"
            ),
            Product(
                name="External Hard Drive",
                description="2TB external hard drive with USB-C connection",
                price=129.99,
                sku="TECH-008"
            ),
            Product(
                name="Wireless Charger",
                description="Fast wireless charger for smartphones and earbuds",
                price=29.99,
                sku="TECH-009"
            ),
            Product(
                name="USB-C Hub",
                description="Multi-port USB-C hub with HDMI and card reader",
                price=49.99,
                sku="TECH-010"
            )
        ]
        
        # Save products
        saved_products = []
        for product in products:
            await product.save()
            saved_products.append(product)
        
        # Create inventory for each product
        for product in saved_products:
            inventory = Inventory(
                product=product,
                quantity=random.randint(10, 100),
                last_restock_date=datetime.now(datetime.now().astimezone().tzinfo) - timedelta(days=random.randint(1, 30))
            )
            await inventory.save()
        
        # Create orders
        for _ in range(20):  # Create 20 orders
            customer = random.choice(saved_customers)
            order_date = datetime.now(datetime.now().astimezone().tzinfo) - timedelta(days=random.randint(1, 60))
            status = random.choice(["pending", "completed", "cancelled"])
            
            order = Order(
                customer=customer,
                order_date=order_date,
                status=status,
                total_amount=0.0  # Will be calculated later
            )
            await order.save()
            
            # Add products to the order
            num_products = random.randint(1, 5)
            order_total = 0.0
            
            # Select random products for this order
            order_products_list = random.sample(saved_products, num_products)
            
            for product in order_products_list:
                quantity = random.randint(1, 3)
                unit_price = product.price
                
                # Add product to order with the through table attributes
                await order.products.add(product, through_defaults={"quantity": quantity, "unit_price": unit_price})
                
                # Update order total
                order_total += unit_price * quantity
            
            # Update the order total
            order.total_amount = order_total
            await order.save()
        
        print("Database seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        raise
    finally:
        # Close Tortoise ORM connections
        await Tortoise.close_connections()

if __name__ == "__main__":
    run_async(seed_database())
