import pytest
from fastapi.testclient import TestClient
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise

from app.main import app
from app.models.models import Customer, Product, Inventory, Order

# Create test client
@pytest.fixture(scope="session")
def client():
    return TestClient(app)

@pytest.fixture(scope="function")
async def test_db():
    """Initialize an in-memory SQLite database for testing."""
    # Define the test config
    test_db_config = {
        "connections": {
            "default": {
                "engine": "tortoise.backends.sqlite",
                "credentials": {"file_path": ":memory:"}
            }
        },
        "apps": {
            "models": {
                "models": ["app.models.models"],
                "default_connection": "default",
            }
        },
        "use_tz": False,
        "timezone": "UTC"
    }
    
    # Close any existing connections first
    try:
        await Tortoise.close_connections()
    except Exception:
        pass
    
    # Initialize Tortoise ORM with the test config
    await Tortoise.init(config=test_db_config)
    
    # Generate the schemas
    await Tortoise.generate_schemas()
    
    # Yield control back to the test
    yield
    
    # Close connections after the test is complete
    await Tortoise.close_connections()

@pytest.fixture(scope="function")
async def test_customer(test_db):
    """Create a test customer for use in tests."""
    customer = await Customer.create(
        name="Test Customer",
        email="test@example.com",
        phone="1234567890",
        address="123 Test St"
    )
    return customer

@pytest.fixture(scope="function")
async def test_product(test_db):
    """Create a test product for use in tests."""
    product = await Product.create(
        name="Test Product",
        description="A test product",
        price=19.99,
        sku="TEST001"
    )
    return product

@pytest.fixture(scope="function")
async def test_inventory(test_db, test_product):
    """Create test inventory for use in tests."""
    inventory = await Inventory.create(
        product=test_product,
        quantity=100
    )
    return inventory

@pytest.fixture(scope="function")
async def test_order(test_db, test_customer, test_product, test_inventory):
    """Create a test order for use in tests."""
    order = await Order.create(
        customer=test_customer,
        total_amount=39.98,
        status="pending"
    )
    # Add order items
    await order.items.add(test_product, through_defaults={"quantity": 2, "unit_price": 19.99})
    return order 