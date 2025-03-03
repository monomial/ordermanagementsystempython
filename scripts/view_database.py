#!/usr/bin/env python3
"""
Script to view the contents of the database.
"""
import sys
import os
from datetime import datetime
from tabulate import tabulate

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.models import Customer, Product, Order, Inventory, order_products

def view_database():
    """View the contents of the database."""
    # Create a new session
    db = SessionLocal()
    
    try:
        # Get all data
        customers = db.query(Customer).all()
        products = db.query(Product).all()
        orders = db.query(Order).all()
        inventories = db.query(Inventory).all()
        
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
            [p.id, p.name, p.description[:30] + "..." if len(p.description) > 30 else p.description, 
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
            product_name = next((p.name for p in products if p.id == inv.product_id), "Unknown")
            restock_date = inv.last_restock_date.strftime('%Y-%m-%d %H:%M:%S') if inv.last_restock_date else "Never"
            inventory_data.append([inv.id, inv.product_id, product_name, inv.quantity, restock_date])
        
        print(tabulate(
            inventory_data,
            headers=["ID", "Product ID", "Product Name", "Quantity", "Last Restock Date"],
            tablefmt="grid"
        ))
        
        # Display orders
        print("\n=== ORDERS ===")
        order_data = []
        for o in orders:
            customer_name = next((c.name for c in customers if c.id == o.customer_id), "Unknown")
            order_data.append([
                o.id, o.customer_id, customer_name, o.order_date.strftime('%Y-%m-%d %H:%M:%S'),
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
        
        # Query the order_products association table
        order_details = db.execute(
            "SELECT op.order_id, op.product_id, p.name, op.quantity, op.unit_price "
            "FROM order_products op "
            "JOIN products p ON op.product_id = p.id"
        ).fetchall()
        
        for od in order_details:
            order_details_data.append([
                od[0],  # order_id
                od[1],  # product_id
                od[2],  # product_name
                od[3],  # quantity
                f"${od[4]:.2f}",  # unit_price
                f"${od[3] * od[4]:.2f}"  # subtotal
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
        db.close()

if __name__ == "__main__":
    view_database()
