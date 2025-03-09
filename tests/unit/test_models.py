import pytest
from datetime import datetime, timezone
from app.models.models import Customer, Product, Inventory, Order, OrderItem

@pytest.mark.asyncio
async def test_customer_model(test_db):
    """Test creating and retrieving a customer."""
    # Create a customer
    customer = await Customer.create(
        name="Test Customer",
        email="test@example.com",
        phone="1234567890",
        address="123 Test St"
    )
    
    # Retrieve the customer
    retrieved_customer = await Customer.get(id=customer.id)
    
    # Assertions
    assert retrieved_customer.id == customer.id
    assert retrieved_customer.name == "Test Customer"
    assert retrieved_customer.email == "test@example.com"
    assert retrieved_customer.phone == "1234567890"
    assert retrieved_customer.address == "123 Test St"
    assert isinstance(retrieved_customer.created_at, datetime)
    assert isinstance(retrieved_customer.updated_at, datetime)

@pytest.mark.asyncio
async def test_product_model(test_db):
    """Test creating and retrieving a product."""
    # Create a product
    product = await Product.create(
        name="Test Product",
        description="A test product",
        price=19.99,
        sku="TEST001"
    )
    
    # Retrieve the product
    retrieved_product = await Product.get(id=product.id)
    
    # Assertions
    assert retrieved_product.id == product.id
    assert retrieved_product.name == "Test Product"
    assert retrieved_product.description == "A test product"
    assert retrieved_product.price == 19.99
    assert retrieved_product.sku == "TEST001"
    assert isinstance(retrieved_product.created_at, datetime)
    assert isinstance(retrieved_product.updated_at, datetime)

@pytest.mark.asyncio
async def test_inventory_model(test_db):
    """Test creating and retrieving inventory."""
    # Create a product first
    product = await Product.create(
        name="Test Product",
        description="A test product",
        price=19.99,
        sku="TEST001"
    )
    
    # Create inventory
    inventory = await Inventory.create(
        product=product,
        quantity=100
    )
    
    # Retrieve the inventory
    retrieved_inventory = await Inventory.get(id=inventory.id).prefetch_related("product")
    
    # Assertions
    assert retrieved_inventory.id == inventory.id
    assert retrieved_inventory.quantity == 100
    assert retrieved_inventory.product.id == product.id
    assert retrieved_inventory.product.name == "Test Product"
    assert isinstance(retrieved_inventory.created_at, datetime)
    assert isinstance(retrieved_inventory.updated_at, datetime)

@pytest.mark.asyncio
async def test_order_model(test_db):
    """Test creating and retrieving an order."""
    # Create a customer
    customer = await Customer.create(
        name="Test Customer",
        email="test@example.com",
        phone="1234567890",
        address="123 Test St"
    )
    
    # Create an order
    order = await Order.create(
        customer=customer,
        status="pending",
        total_amount=39.98
    )
    
    # Retrieve the order
    retrieved_order = await Order.get(id=order.id).prefetch_related("customer")
    
    # Assertions
    assert retrieved_order.id == order.id
    assert retrieved_order.status == "pending"
    assert retrieved_order.total_amount == 39.98
    assert retrieved_order.customer.id == customer.id
    assert retrieved_order.customer.name == "Test Customer"
    assert isinstance(retrieved_order.created_at, datetime)
    assert isinstance(retrieved_order.updated_at, datetime)

@pytest.mark.asyncio
async def test_order_with_items(test_db):
    """Test creating an order with items."""
    # Create a customer
    customer = await Customer.create(
        name="Test Customer",
        email="test@example.com",
        phone="1234567890",
        address="123 Test St"
    )
    
    # Create a product
    product = await Product.create(
        name="Test Product",
        description="A test product",
        price=19.99,
        sku="TEST001"
    )
    
    # Create inventory for the product
    await Inventory.create(
        product=product,
        quantity=100
    )
    
    # Create an order
    order = await Order.create(
        customer=customer,
        status="pending",
        total_amount=39.98
    )
    
    # Create an order item
    order_item = await OrderItem.create(
        order=order,
        product=product,
        quantity=2,
        unit_price=19.99,
        subtotal=39.98
    )
    
    # Retrieve the order with items
    retrieved_order = await Order.get(id=order.id).prefetch_related("items__product")
    
    # Assertions
    assert retrieved_order.id == order.id
    assert len(await retrieved_order.items.all()) == 1
    
    # Get the order item
    order_items = await retrieved_order.items.all().prefetch_related("product")
    assert len(order_items) == 1
    
    item = order_items[0]
    assert item.quantity == 2
    assert item.unit_price == 19.99
    assert item.subtotal == 39.98
    assert item.product.id == product.id
    assert item.product.name == "Test Product"

@pytest.mark.asyncio
async def test_relationships(test_db):
    """Test the relationships between models."""
    # Create a customer
    customer = await Customer.create(
        name="Test Customer",
        email="test@example.com",
        phone="1234567890",
        address="123 Test St"
    )
    
    # Create a product
    product = await Product.create(
        name="Test Product",
        description="A test product",
        price=19.99,
        sku="TEST001"
    )
    
    # Create inventory for the product
    inventory = await Inventory.create(
        product=product,
        quantity=100
    )
    
    # Create an order
    order = await Order.create(
        customer=customer,
        status="pending",
        total_amount=39.98
    )
    
    # Create an order item
    order_item = await OrderItem.create(
        order=order,
        product=product,
        quantity=2,
        unit_price=19.99,
        subtotal=39.98
    )
    
    # Test customer -> orders relationship
    customer_orders = await customer.orders.all()
    assert len(customer_orders) == 1
    assert customer_orders[0].id == order.id
    
    # Test product -> order_items relationship
    product_order_items = await product.order_items.all()
    assert len(product_order_items) == 1
    assert product_order_items[0].id == order_item.id
    
    # Test product -> inventory relationship
    product_inventory = await product.inventory
    assert product_inventory.id == inventory.id
    assert product_inventory.quantity == 100 