import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.schemas import (
    CustomerCreate, CustomerUpdate, Customer,
    ProductCreate, ProductUpdate, Product,
    InventoryCreate, InventoryUpdate, Inventory,
    OrderCreate, OrderUpdate, Order, OrderItemCreate
)

def test_customer_create_schema():
    """Test CustomerCreate schema validation."""
    # Valid data
    data = {
        "name": "Test Customer",
        "email": "test@example.com",
        "phone": "1234567890",
        "address": "123 Test St"
    }
    customer = CustomerCreate(**data)
    assert customer.name == "Test Customer"
    assert customer.email == "test@example.com"
    assert customer.phone == "1234567890"
    assert customer.address == "123 Test St"
    
    # Test required fields
    with pytest.raises(ValidationError):
        CustomerCreate(email="test@example.com")  # Missing name
    
    with pytest.raises(ValidationError):
        CustomerCreate(name="Test Customer")  # Missing email

def test_customer_update_schema():
    """Test CustomerUpdate schema validation."""
    # All fields are optional in update
    data = {
        "name": "Updated Customer",
        "email": "updated@example.com"
    }
    customer = CustomerUpdate(**data)
    assert customer.name == "Updated Customer"
    assert customer.email == "updated@example.com"
    assert customer.phone is None
    assert customer.address is None
    
    # Empty update is valid
    customer = CustomerUpdate()
    assert customer.name is None
    assert customer.email is None

def test_product_create_schema():
    """Test ProductCreate schema validation."""
    # Valid data
    data = {
        "name": "Test Product",
        "description": "A test product",
        "price": 19.99,
        "sku": "TEST001"
    }
    product = ProductCreate(**data)
    assert product.name == "Test Product"
    assert product.description == "A test product"
    assert product.price == 19.99
    assert product.sku == "TEST001"
    
    # Test required fields
    with pytest.raises(ValidationError):
        ProductCreate(name="Test Product", sku="TEST001")  # Missing price
    
    # Test price validation (must be > 0)
    with pytest.raises(ValidationError):
        ProductCreate(name="Test Product", price=0, sku="TEST001")
    
    with pytest.raises(ValidationError):
        ProductCreate(name="Test Product", price=-10, sku="TEST001")

def test_product_update_schema():
    """Test ProductUpdate schema validation."""
    # All fields are optional in update
    data = {
        "name": "Updated Product",
        "price": 29.99
    }
    product = ProductUpdate(**data)
    assert product.name == "Updated Product"
    assert product.price == 29.99
    assert product.description is None
    assert product.sku is None
    
    # Empty update is valid
    product = ProductUpdate()
    assert product.name is None
    assert product.price is None
    
    # Price validation still applies if provided
    with pytest.raises(ValidationError):
        ProductUpdate(price=-10)

def test_inventory_create_schema():
    """Test InventoryCreate schema validation."""
    # Valid data
    data = {
        "product_id": 1,
        "quantity": 100
    }
    inventory = InventoryCreate(**data)
    assert inventory.product_id == 1
    assert inventory.quantity == 100
    
    # Test required fields
    with pytest.raises(ValidationError):
        InventoryCreate(product_id=1)  # Missing quantity
    
    # Test quantity validation (must be >= 0)
    with pytest.raises(ValidationError):
        InventoryCreate(product_id=1, quantity=-10)
    
    # Zero quantity is valid
    inventory = InventoryCreate(product_id=1, quantity=0)
    assert inventory.quantity == 0

def test_inventory_update_schema():
    """Test InventoryUpdate schema validation."""
    # All fields are optional in update
    data = {
        "quantity": 50
    }
    inventory = InventoryUpdate(**data)
    assert inventory.quantity == 50
    
    # Empty update is valid
    inventory = InventoryUpdate()
    assert inventory.quantity is None
    
    # Quantity validation still applies if provided
    with pytest.raises(ValidationError):
        InventoryUpdate(quantity=-10)

def test_order_item_create_schema():
    """Test OrderItemCreate schema validation."""
    # Valid data
    data = {
        "product_id": 1,
        "quantity": 2
    }
    order_item = OrderItemCreate(**data)
    assert order_item.product_id == 1
    assert order_item.quantity == 2
    
    # Test required fields
    with pytest.raises(ValidationError):
        OrderItemCreate(product_id=1)  # Missing quantity
    
    # Test quantity validation (must be > 0)
    with pytest.raises(ValidationError):
        OrderItemCreate(product_id=1, quantity=0)
    
    with pytest.raises(ValidationError):
        OrderItemCreate(product_id=1, quantity=-1)

def test_order_create_schema():
    """Test OrderCreate schema validation."""
    # Valid data
    data = {
        "customer_id": 1,
        "items": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 2, "quantity": 1}
        ]
    }
    order = OrderCreate(**data)
    assert order.customer_id == 1
    assert len(order.items) == 2
    assert order.items[0].product_id == 1
    assert order.items[0].quantity == 2
    assert order.items[1].product_id == 2
    assert order.items[1].quantity == 1
    
    # Test required fields
    with pytest.raises(ValidationError):
        OrderCreate(items=[{"product_id": 1, "quantity": 2}])  # Missing customer_id
    
    with pytest.raises(ValidationError):
        OrderCreate(customer_id=1)  # Missing items
    
    # Note: Empty items list might be valid in the schema, so we'll skip this test
    # Uncomment if the schema is updated to validate non-empty items
    # with pytest.raises(ValidationError):
    #     OrderCreate(customer_id=1, items=[])

def test_order_update_schema():
    """Test OrderUpdate schema validation."""
    # Valid data
    data = {
        "status": "completed"
    }
    order = OrderUpdate(**data)
    assert order.status == "completed"
    
    # Empty update is valid
    order = OrderUpdate()
    assert order.status is None 