from app.models.models import Customer, Product, Order, Inventory, OrderItem
from datetime import datetime
import asyncio
from tortoise import Tortoise
from app.db.database import SQLALCHEMY_DATABASE_URL

def format_datetime(dt):
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return "N/A"

def print_separator(char="-", length=80):
    print(char * length)

async def init_db():
    # Initialize Tortoise ORM using the same URL as the rest of the application
    await Tortoise.init(
        db_url=SQLALCHEMY_DATABASE_URL,
        modules={"models": ["app.models.models"]}
    )

async def query_database():
    try:
        # 1. Customers
        print("\n=== CUSTOMERS ===")
        print_separator()
        print(f"{'ID':<5} {'Name':<20} {'Email':<30} {'Phone':<15} {'Address':<30}")
        print_separator()
        customers = await Customer.all()
        for customer in customers:
            print(f"{customer.id:<5} {customer.name[:20]:<20} {customer.email[:30]:<30} {(customer.phone or 'N/A')[:15]:<15} {(customer.address or 'N/A')[:30]:<30}")

        # 2. Products
        print("\n=== PRODUCTS ===")
        print_separator()
        print(f"{'ID':<5} {'Name':<20} {'SKU':<15} {'Price':<10} {'Description':<30}")
        print_separator()
        products = await Product.all()
        for product in products:
            print(f"{product.id:<5} {product.name[:20]:<20} {product.sku[:15]:<15} ${product.price:<9.2f} {(product.description or 'N/A')[:30]:<30}")

        # 3. Inventory
        print("\n=== INVENTORY ===")
        print_separator()
        print(f"{'ID':<5} {'Product Name':<20} {'Quantity':<10} {'Last Restock Date':<20}")
        print_separator()
        inventory_items = await Inventory.all().prefetch_related('product')
        for item in inventory_items:
            print(f"{item.id:<5} {item.product.name[:20]:<20} {item.quantity:<10} {format_datetime(item.last_restock_date):<20}")

        # 4. Orders
        print("\n=== ORDERS ===")
        print_separator()
        print(f"{'ID':<5} {'Customer':<20} {'Status':<10} {'Total Amount':<12} {'Order Date':<20}")
        print_separator()
        orders = await Order.all().prefetch_related('customer', 'items__product')
        for order in orders:
            print(f"{order.id:<5} {order.customer.name[:20]:<20} {order.status:<10} ${order.total_amount:<11.2f} {format_datetime(order.order_date):<20}")
            
            # Display order items
            if hasattr(order, 'items') and order.items:
                print(f"\t{'Product':<20} {'Quantity':<10} {'Unit Price':<12} {'Subtotal':<12}")
                print(f"\t{'-' * 58}")
                for item in order.items:
                    print(f"\t{item.product.name[:20]:<20} {item.quantity:<10} ${item.unit_price:<11.2f} ${item.subtotal:<11.2f}")
            else:
                print("\tNo items in this order")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

async def main():
    await init_db()
    await query_database()
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(main()) 