import pytest
from fastapi.testclient import TestClient
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise

from app.main import app, API_V1_PREFIX
from app.models.models import Customer, Product, Inventory, Order

# Create test client
client = TestClient(app)

@pytest.fixture(scope="function")
async def test_db():
    # Initialize Tortoise ORM
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["app.models.models"]}
    )
    # Create the tables
    await Tortoise.generate_schemas()
    yield
    # Drop the tables after the test
    await Tortoise.close_connections()

@pytest.mark.asyncio
async def test_create_customer(test_db):
    response = client.post(
        f"{API_V1_PREFIX}/customers/",
        json={"name": "Test Customer", "email": "test@example.com", "phone": "1234567890", "address": "123 Test St"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Customer"
    assert data["email"] == "test@example.com"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_product(test_db):
    response = client.post(
        f"{API_V1_PREFIX}/products/",
        json={"name": "Test Product", "description": "A test product", "price": 19.99, "sku": "TEST001"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Product"
    assert data["price"] == 19.99
    assert "id" in data

@pytest.mark.asyncio
async def test_create_inventory(test_db):
    # First create a product
    product_response = client.post(
        f"{API_V1_PREFIX}/products/",
        json={"name": "Test Product", "description": "A test product", "price": 19.99, "sku": "TEST001"},
    )
    product_id = product_response.json()["id"]
    
    # Then create inventory for the product
    response = client.post(
        f"{API_V1_PREFIX}/inventory/",
        json={"product_id": product_id, "quantity": 100},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["product_id"] == product_id
    assert data["quantity"] == 100

@pytest.mark.asyncio
async def test_create_order(test_db):
    # Create a customer
    customer_response = client.post(
        f"{API_V1_PREFIX}/customers/",
        json={"name": "Test Customer", "email": "test@example.com", "phone": "1234567890", "address": "123 Test St"},
    )
    customer_id = customer_response.json()["id"]
    
    # Create a product
    product_response = client.post(
        f"{API_V1_PREFIX}/products/",
        json={"name": "Test Product", "description": "A test product", "price": 19.99, "sku": "TEST001"},
    )
    product_id = product_response.json()["id"]
    
    # Create inventory for the product
    client.post(
        f"{API_V1_PREFIX}/inventory/",
        json={"product_id": product_id, "quantity": 100},
    )
    
    # Create an order
    response = client.post(
        f"{API_V1_PREFIX}/orders/",
        json={
            "customer_id": customer_id,
            "items": [{"product_id": product_id, "quantity": 2}]
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == customer_id
    assert data["total_amount"] == 39.98  # 19.99 * 2
    assert "id" in data 