import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app, API_V1_PREFIX
from app.db.database import Base, get_db
from app.models.models import Customer, Product, Inventory, Order

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

@pytest.fixture(scope="function")
def test_db():
    # Create the tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop the tables after the test
    Base.metadata.drop_all(bind=engine)

def test_create_customer(test_db):
    response = client.post(
        f"{API_V1_PREFIX}/customers/",
        json={"name": "Test Customer", "email": "test@example.com", "phone": "1234567890", "address": "123 Test St"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Customer"
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_create_product(test_db):
    response = client.post(
        f"{API_V1_PREFIX}/products/",
        json={"name": "Test Product", "description": "A test product", "price": 19.99, "sku": "TEST001"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Product"
    assert data["price"] == 19.99
    assert "id" in data

def test_create_inventory(test_db):
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

def test_create_order(test_db):
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