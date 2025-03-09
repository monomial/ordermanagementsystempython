import pytest
from fastapi.testclient import TestClient
from app.main import app, API_V1_PREFIX

# Create test client
client = TestClient(app)

# Customer API Tests
@pytest.mark.asyncio
async def test_create_customer(test_db):
    """Test creating a customer."""
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
async def test_get_customer(test_db):
    """Test retrieving a customer."""
    # First create a customer
    create_response = client.post(
        f"{API_V1_PREFIX}/customers/",
        json={"name": "Test Customer", "email": "test@example.com", "phone": "1234567890", "address": "123 Test St"},
    )
    customer_id = create_response.json()["id"]
    
    # Then get the customer
    response = client.get(f"{API_V1_PREFIX}/customers/{customer_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == customer_id
    assert data["name"] == "Test Customer"
    assert data["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_update_customer(test_db):
    """Test updating a customer."""
    # First create a customer
    create_response = client.post(
        f"{API_V1_PREFIX}/customers/",
        json={"name": "Test Customer", "email": "test@example.com", "phone": "1234567890", "address": "123 Test St"},
    )
    customer_id = create_response.json()["id"]
    
    # Then update the customer
    response = client.put(
        f"{API_V1_PREFIX}/customers/{customer_id}",
        json={"name": "Updated Customer", "email": "updated@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == customer_id
    assert data["name"] == "Updated Customer"
    assert data["email"] == "updated@example.com"
    
    # Verify the update
    get_response = client.get(f"{API_V1_PREFIX}/customers/{customer_id}")
    assert get_response.json()["name"] == "Updated Customer"

@pytest.mark.asyncio
async def test_delete_customer(test_db):
    """Test deleting a customer."""
    # First create a customer
    create_response = client.post(
        f"{API_V1_PREFIX}/customers/",
        json={"name": "Test Customer", "email": "test@example.com", "phone": "1234567890", "address": "123 Test St"},
    )
    customer_id = create_response.json()["id"]
    
    # Then delete the customer
    response = client.delete(f"{API_V1_PREFIX}/customers/{customer_id}")
    assert response.status_code == 200
    
    # Verify the customer is deleted
    get_response = client.get(f"{API_V1_PREFIX}/customers/{customer_id}")
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_get_all_customers(test_db):
    """Test retrieving all customers."""
    # Create multiple customers
    client.post(
        f"{API_V1_PREFIX}/customers/",
        json={"name": "Customer 1", "email": "customer1@example.com"},
    )
    client.post(
        f"{API_V1_PREFIX}/customers/",
        json={"name": "Customer 2", "email": "customer2@example.com"},
    )
    
    # Get all customers
    response = client.get(f"{API_V1_PREFIX}/customers/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    
    # Check if the created customers are in the list
    emails = [customer["email"] for customer in data]
    assert "customer1@example.com" in emails
    assert "customer2@example.com" in emails

# Product API Tests
@pytest.mark.asyncio
async def test_create_product(test_db):
    """Test creating a product."""
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
async def test_get_product(test_db):
    """Test retrieving a product."""
    # First create a product
    create_response = client.post(
        f"{API_V1_PREFIX}/products/",
        json={"name": "Test Product", "description": "A test product", "price": 19.99, "sku": "TEST001"},
    )
    product_id = create_response.json()["id"]
    
    # Then get the product
    response = client.get(f"{API_V1_PREFIX}/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == "Test Product"
    assert data["price"] == 19.99

@pytest.mark.asyncio
async def test_update_product(test_db):
    """Test updating a product."""
    # First create a product
    create_response = client.post(
        f"{API_V1_PREFIX}/products/",
        json={"name": "Test Product", "description": "A test product", "price": 19.99, "sku": "TEST001"},
    )
    product_id = create_response.json()["id"]
    
    # Then update the product
    response = client.put(
        f"{API_V1_PREFIX}/products/{product_id}",
        json={"name": "Updated Product", "price": 29.99},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == "Updated Product"
    assert data["price"] == 29.99
    
    # Verify the update
    get_response = client.get(f"{API_V1_PREFIX}/products/{product_id}")
    assert get_response.json()["name"] == "Updated Product"

@pytest.mark.asyncio
async def test_delete_product(test_db):
    """Test deleting a product."""
    # First create a product
    create_response = client.post(
        f"{API_V1_PREFIX}/products/",
        json={"name": "Test Product", "description": "A test product", "price": 19.99, "sku": "TEST001"},
    )
    product_id = create_response.json()["id"]
    
    # Then delete the product
    response = client.delete(f"{API_V1_PREFIX}/products/{product_id}")
    assert response.status_code == 200
    
    # Verify the product is deleted
    get_response = client.get(f"{API_V1_PREFIX}/products/{product_id}")
    assert get_response.status_code == 404

# Inventory API Tests
@pytest.mark.asyncio
async def test_create_inventory(test_db):
    """Test creating inventory."""
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
async def test_get_inventory(test_db):
    """Test retrieving inventory."""
    # First create a product and inventory
    product_response = client.post(
        f"{API_V1_PREFIX}/products/",
        json={"name": "Test Product", "description": "A test product", "price": 19.99, "sku": "TEST001"},
    )
    product_id = product_response.json()["id"]
    
    inventory_response = client.post(
        f"{API_V1_PREFIX}/inventory/",
        json={"product_id": product_id, "quantity": 100},
    )
    inventory_id = inventory_response.json()["id"]
    
    # Then get the inventory
    response = client.get(f"{API_V1_PREFIX}/inventory/{inventory_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == inventory_id
    assert data["product_id"] == product_id
    assert data["quantity"] == 100

@pytest.mark.asyncio
async def test_update_inventory(test_db):
    """Test updating inventory."""
    # First create a product and inventory
    product_response = client.post(
        f"{API_V1_PREFIX}/products/",
        json={"name": "Test Product", "description": "A test product", "price": 19.99, "sku": "TEST001"},
    )
    product_id = product_response.json()["id"]
    
    inventory_response = client.post(
        f"{API_V1_PREFIX}/inventory/",
        json={"product_id": product_id, "quantity": 100},
    )
    inventory_id = inventory_response.json()["id"]
    
    # Then update the inventory
    response = client.put(
        f"{API_V1_PREFIX}/inventory/{inventory_id}",
        json={"quantity": 50},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == inventory_id
    assert data["quantity"] == 50
    
    # Verify the update
    get_response = client.get(f"{API_V1_PREFIX}/inventory/{inventory_id}")
    assert get_response.json()["quantity"] == 50

# Order API Tests
@pytest.mark.asyncio
async def test_create_order(test_db):
    """Test creating an order."""
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

@pytest.mark.asyncio
async def test_get_order(test_db):
    """Test retrieving an order."""
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
    order_response = client.post(
        f"{API_V1_PREFIX}/orders/",
        json={
            "customer_id": customer_id,
            "items": [{"product_id": product_id, "quantity": 2}]
        },
    )
    order_id = order_response.json()["id"]
    
    # Get the order
    response = client.get(f"{API_V1_PREFIX}/orders/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert data["customer_id"] == customer_id
    assert data["total_amount"] == 39.98
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == product_id
    assert data["items"][0]["quantity"] == 2

@pytest.mark.asyncio
async def test_update_order_status(test_db):
    """Test updating an order status."""
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
    order_response = client.post(
        f"{API_V1_PREFIX}/orders/",
        json={
            "customer_id": customer_id,
            "items": [{"product_id": product_id, "quantity": 2}]
        },
    )
    order_id = order_response.json()["id"]
    
    # Update the order status
    response = client.put(
        f"{API_V1_PREFIX}/orders/{order_id}",
        json={"status": "completed"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert data["status"] == "completed"
    
    # Verify the update
    get_response = client.get(f"{API_V1_PREFIX}/orders/{order_id}")
    assert get_response.json()["status"] == "completed"

@pytest.mark.asyncio
async def test_error_handling_invalid_product(test_db):
    """Test error handling for invalid product ID."""
    # Create a customer
    customer_response = client.post(
        f"{API_V1_PREFIX}/customers/",
        json={"name": "Test Customer", "email": "test@example.com", "phone": "1234567890", "address": "123 Test St"},
    )
    customer_id = customer_response.json()["id"]
    
    # Try to create an order with an invalid product ID
    response = client.post(
        f"{API_V1_PREFIX}/orders/",
        json={
            "customer_id": customer_id,
            "items": [{"product_id": 9999, "quantity": 2}]  # Invalid product ID
        },
    )
    assert response.status_code == 404  # Not Found

@pytest.mark.asyncio
async def test_error_handling_insufficient_inventory(test_db):
    """Test error handling for insufficient inventory."""
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
    
    # Create inventory with low quantity
    client.post(
        f"{API_V1_PREFIX}/inventory/",
        json={"product_id": product_id, "quantity": 1},
    )
    
    # Try to order more than available
    response = client.post(
        f"{API_V1_PREFIX}/orders/",
        json={
            "customer_id": customer_id,
            "items": [{"product_id": product_id, "quantity": 10}]  # More than available
        },
    )
    assert response.status_code == 400  # Bad Request 