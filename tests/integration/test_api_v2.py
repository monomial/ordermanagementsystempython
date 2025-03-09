import pytest
from fastapi.testclient import TestClient
from app.main import app, API_V2_PREFIX, API_V1_PREFIX

# Create test client
client = TestClient(app)

@pytest.mark.asyncio
async def test_get_product_v2(test_db):
    """Test retrieving a product using the v2 API."""
    # First create a product using v1 API
    create_response = client.post(
        f"{API_V1_PREFIX}/products/",
        json={"name": "Test Product", "description": "A test product", "price": 19.99, "sku": "TEST001"},
    )
    product_id = create_response.json()["id"]
    
    # Then get the product using v2 API
    response = client.get(f"{API_V2_PREFIX}/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == "Test Product"
    assert data["price"] == 19.99

@pytest.mark.asyncio
async def test_get_products_pagination(test_db):
    """Test the pagination of products in the v2 API."""
    # Create multiple products
    for i in range(15):  # Create 15 products
        client.post(
            f"{API_V1_PREFIX}/products/",
            json={
                "name": f"Product {i+1}",
                "description": f"Description for product {i+1}",
                "price": 10.0 + i,
                "sku": f"SKU{i+1:03d}"
            },
        )
    
    # Test first page with default page size (10)
    response = client.get(f"{API_V2_PREFIX}/products/")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_items"] >= 15
    assert data["total_pages"] >= 2
    assert data["has_next"] == True
    assert data["has_prev"] == False
    assert len(data["items"]) == 10
    
    # Test second page
    response = client.get(f"{API_V2_PREFIX}/products/?page=2")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["has_prev"] == True
    assert len(data["items"]) >= 5  # At least 5 items on the second page
    
    # Test custom page size
    response = client.get(f"{API_V2_PREFIX}/products/?page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert data["page_size"] == 5
    assert data["total_pages"] >= 3
    assert len(data["items"]) == 5

@pytest.mark.asyncio
async def test_filter_products_by_name(test_db):
    """Test filtering products by name in the v2 API."""
    # Create products with specific names
    client.post(
        f"{API_V1_PREFIX}/products/",
        json={"name": "Apple iPhone", "description": "A smartphone", "price": 999.99, "sku": "IPHONE001"},
    )
    client.post(
        f"{API_V1_PREFIX}/products/",
        json={"name": "Samsung Galaxy", "description": "Another smartphone", "price": 899.99, "sku": "GALAXY001"},
    )
    
    # Filter by name
    response = client.get(f"{API_V2_PREFIX}/products/?name=iPhone")
    assert response.status_code == 200
    data = response.json()
    
    # Check that only iPhone is returned
    assert len(data["items"]) >= 1
    assert any("iPhone" in item["name"] for item in data["items"])
    assert not any("Galaxy" in item["name"] for item in data["items"])

@pytest.mark.asyncio
async def test_filter_products_by_price(test_db):
    """Test filtering products by price range in the v2 API."""
    # Create products with different prices
    client.post(
        f"{API_V1_PREFIX}/products/",
        json={"name": "Budget Phone", "description": "Affordable phone", "price": 199.99, "sku": "BUDGET001"},
    )
    client.post(
        f"{API_V1_PREFIX}/products/",
        json={"name": "Mid-range Phone", "description": "Mid-range phone", "price": 499.99, "sku": "MIDRANGE001"},
    )
    client.post(
        f"{API_V1_PREFIX}/products/",
        json={"name": "Premium Phone", "description": "High-end phone", "price": 999.99, "sku": "PREMIUM001"},
    )
    
    # Filter by min price
    response = client.get(f"{API_V2_PREFIX}/products/?min_price=500")
    assert response.status_code == 200
    data = response.json()
    
    # Check that only premium phones are returned
    for item in data["items"]:
        assert item["price"] >= 500
    
    # Filter by max price
    response = client.get(f"{API_V2_PREFIX}/products/?max_price=200")
    assert response.status_code == 200
    data = response.json()
    
    # Check that only budget phones are returned
    for item in data["items"]:
        assert item["price"] <= 200
    
    # Filter by price range
    response = client.get(f"{API_V2_PREFIX}/products/?min_price=300&max_price=700")
    assert response.status_code == 200
    data = response.json()
    
    # Check that only mid-range phones are returned
    for item in data["items"]:
        assert item["price"] >= 300
        assert item["price"] <= 700

@pytest.mark.asyncio
async def test_combined_filters(test_db):
    """Test combining multiple filters in the v2 API."""
    # Create various products
    client.post(
        f"{API_V1_PREFIX}/products/",
        json={"name": "Budget Android", "description": "Affordable Android phone", "price": 199.99, "sku": "BUDGETAND001"},
    )
    client.post(
        f"{API_V1_PREFIX}/products/",
        json={"name": "Premium Android", "description": "High-end Android phone", "price": 899.99, "sku": "PREMIUMAND001"},
    )
    client.post(
        f"{API_V1_PREFIX}/products/",
        json={"name": "Budget iPhone", "description": "Affordable iPhone", "price": 399.99, "sku": "BUDGETIPH001"},
    )
    client.post(
        f"{API_V1_PREFIX}/products/",
        json={"name": "Premium iPhone", "description": "High-end iPhone", "price": 1099.99, "sku": "PREMIUMIPH001"},
    )
    
    # Combine name and price filters
    response = client.get(f"{API_V2_PREFIX}/products/?name=iPhone&min_price=1000")
    assert response.status_code == 200
    data = response.json()
    
    # Check that only premium iPhones are returned
    for item in data["items"]:
        assert "iPhone" in item["name"]
        assert item["price"] >= 1000

@pytest.mark.asyncio
async def test_error_handling_invalid_page(test_db):
    """Test error handling for invalid page parameters."""
    # Test with invalid page number (negative)
    response = client.get(f"{API_V2_PREFIX}/products/?page=-1")
    assert response.status_code == 422  # Unprocessable Entity
    
    # Test with invalid page size (too large)
    response = client.get(f"{API_V2_PREFIX}/products/?page_size=1000")
    assert response.status_code == 422  # Unprocessable Entity

@pytest.mark.asyncio
async def test_error_handling_invalid_product_id(test_db):
    """Test error handling for invalid product ID."""
    # Test with non-existent product ID
    response = client.get(f"{API_V2_PREFIX}/products/9999")
    assert response.status_code == 404  # Not Found 