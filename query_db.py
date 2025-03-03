from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Customer, Product, Order, Inventory
from datetime import datetime

def format_datetime(dt):
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return "N/A"

def print_separator(char="-", length=80):
    print(char * length)

def query_database():
    # Create database connection
    engine = create_engine("sqlite:///order_management.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 1. Customers
        print("\n=== CUSTOMERS ===")
        print_separator()
        print(f"{'ID':<5} {'Name':<20} {'Email':<30} {'Phone':<15} {'Address':<30}")
        print_separator()
        customers = session.query(Customer).all()
        for customer in customers:
            print(f"{customer.id:<5} {customer.name[:20]:<20} {customer.email[:30]:<30} {(customer.phone or 'N/A')[:15]:<15} {(customer.address or 'N/A')[:30]:<30}")

        # 2. Products
        print("\n=== PRODUCTS ===")
        print_separator()
        print(f"{'ID':<5} {'Name':<20} {'SKU':<15} {'Price':<10} {'Description':<30}")
        print_separator()
        products = session.query(Product).all()
        for product in products:
            print(f"{product.id:<5} {product.name[:20]:<20} {product.sku[:15]:<15} ${product.price:<9.2f} {(product.description or 'N/A')[:30]:<30}")

        # 3. Inventory
        print("\n=== INVENTORY ===")
        print_separator()
        print(f"{'ID':<5} {'Product Name':<20} {'Quantity':<10} {'Last Restock Date':<20}")
        print_separator()
        inventory = session.query(Inventory).all()
        for item in inventory:
            print(f"{item.id:<5} {item.product.name[:20]:<20} {item.quantity:<10} {format_datetime(item.last_restock_date):<20}")

        # 4. Orders
        print("\n=== ORDERS ===")
        print_separator()
        print(f"{'ID':<5} {'Customer':<20} {'Status':<10} {'Total Amount':<12} {'Order Date':<20}")
        print_separator()
        orders = session.query(Order).all()
        for order in orders:
            print(f"{order.id:<5} {order.customer.name[:20]:<20} {order.status:<10} ${order.total_amount:<11.2f} {format_datetime(order.order_date):<20}")

            # Show order details
            if order.products:
                print("\tOrder Items:")
                for product in order.products:
                    # Get quantity and unit price from order_products table
                    order_product = next(p for p in order.products if p.id == product.id)
                    print(f"\t- {product.name[:30]:<30} (Qty: {order_product.quantity}, Price: ${product.price:.2f})")
                print()

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    query_database() 