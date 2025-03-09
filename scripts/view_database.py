#!/usr/bin/env python3
"""
Script to view the contents of the database using Tortoise ORM.
"""
import sys
import os
from datetime import datetime
from tabulate import tabulate
import asyncio

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tortoise import Tortoise, run_async
from app.db.database import DATABASE_URL
from app.models.models import Customer, Product, Order, Inventory

# Convert URL to Tortoise format if needed
DB_URL = DATABASE_URL.replace('sqlite:///./','sqlite://')

async def init_tortoise():
    """Initialize Tortoise ORM."""
    await Tortoise.init(
        db_url=DB_URL,
        modules={"models": ["app.models.models"]}
    )

async def view_database():
    """View the contents of the database."""
    # Initialize Tortoise ORM
    await init_tortoise()
    
    try:
        # Get all data
        customers = await Customer.all()
        products = await Product.all()
        orders = await Order.all().prefetch_related('customer')
        inventories = await Inventory.all().prefetch_related('product')
        
        # Display customers
        print("\n=== CUSTOMERS ===")
        customer_data = [
            [c.id, c.name, c.email, c.phone, c.address, 
             c.notes if c.notes else "N/A", 
             c.created_at.strftime('%Y-%m-%d %H:%M:%S')]
            for c in customers
        ]
        print(tabulate(
            customer_data,
            headers=["ID", "Name", "Email", "Phone", "Address", "Notes", "Created At"],
            tablefmt="grid"
        ))
        
        # Display products
        print("\n=== PRODUCTS ===")
        product_data = [
            [p.id, p.name, p.description[:30] + "..." if p.description and len(p.description) > 30 else p.description, 
             f"${p.price:.2f}", p.sku, p.created_at.strftime('%Y-%m-%d %H:%M:%S')]
            for p in products
        ]
        print(tabulate(
            product_data,
            headers=["ID", "Name", "Description", "Price", "SKU", "Created At"],
            tablefmt="grid"
        ))
        
        # Display inventory
        print("\n=== INVENTORY ===")
        inventory_data = []
        for inv in inventories:
            restock_date = inv.last_restock_date.strftime('%Y-%m-%d %H:%M:%S') if inv.last_restock_date else "Never"
            inventory_data.append([inv.id, inv.product.id, inv.product.name, inv.quantity, restock_date])
        
        print(tabulate(
            inventory_data,
            headers=["ID", "Product ID", "Product Name", "Quantity", "Last Restock Date"],
            tablefmt="grid"
        ))
        
        # Display orders
        print("\n=== ORDERS ===")
        order_data = []
        for o in orders:
            order_data.append([
                o.id, o.customer.id, o.customer.name, o.order_date.strftime('%Y-%m-%d %H:%M:%S'),
                o.status, f"${o.total_amount:.2f}"
            ])
        
        print(tabulate(
            order_data,
            headers=["ID", "Customer ID", "Customer Name", "Order Date", "Status", "Total Amount"],
            tablefmt="grid"
        ))
        
        # Display order details
        print("\n=== ORDER DETAILS ===")
        order_details_data = []
        
        # Get all orders with their items
        orders_with_items = await Order.all().prefetch_related('items', 'items__product')
        
        for order in orders_with_items:
            # Get the order items
            for item in order.items:
                order_details_data.append([
                    order.id,
                    item.product.id,
                    item.product.name,
                    item.quantity,
                    f"${item.unit_price:.2f}",
                    f"${item.subtotal:.2f}"  # subtotal
                ])
        
        print(tabulate(
            order_details_data,
            headers=["Order ID", "Product ID", "Product Name", "Quantity", "Unit Price", "Subtotal"],
            tablefmt="grid"
        ))
        
    except Exception as e:
        print(f"Error viewing database: {e}")
        raise
    finally:
        # Close Tortoise ORM connections
        await Tortoise.close_connections()

if __name__ == "__main__":
    run_async(view_database())
