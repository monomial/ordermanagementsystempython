import pytest
from fastapi.testclient import TestClient

from app.main import app, API_V2_PREFIX
from tests.test_api import test_db  # Reuse the test_db fixture

# Create test client
client = TestClient(app)

def test_read_products_pagination(test_db):
    # First, create multiple products
    products_to_create = [
        {"name": f"Test Product {i}", "description": f"Description {i}", "price": 10.0 + i, "sku": f"SKU{i:03d}"}
        for i in range(1, 16)  # Create 15 products
    ]
    
    for product in products_to_create:
        client.post(f"/api/v1/products/", json=product)
    
    # Test default pagination (page 1, page_size 10)
    response = client.get(f"{API_V2_PREFIX}/products/")
    assert response.status_code == 200
    data = response.json()
    
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_items"] == 15
    assert data["total_pages"] == 2
    assert data["has_next"] == True
    assert data["has_prev"] == False
    assert len(data["items"]) == 10
    
    # Test page 2
    response = client.get(f"{API_V2_PREFIX}/products/?page=2")
    assert response.status_code == 200
    data = response.json()
    
    assert data["page"] == 2
    assert data["page_size"] == 10
    assert data["total_items"] == 15
    assert data["total_pages"] == 2
    assert data["has_next"] == False
    assert data["has_prev"] == True
    assert len(data["items"]) == 5
    
    # Test custom page_size
    response = client.get(f"{API_V2_PREFIX}/products/?page_size=5")
    assert response.status_code == 200
    data = response.json()
    
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert data["total_items"] == 15
    assert data["total_pages"] == 3
    assert len(data["items"]) == 5
    
    # Test filtering by name
    response = client.get(f"{API_V2_PREFIX}/products/?name=Product%201")
    assert response.status_code == 200
    data = response.json()
    
    # Should match "Test Product 1", "Test Product 10", "Test Product 11", etc.
    assert data["total_items"] > 0
    for item in data["items"]:
        assert "Product 1" in item["name"]
    
    # Test filtering by price range
    response = client.get(f"{API_V2_PREFIX}/products/?min_price=12&max_price=15")
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_items"] > 0
    for item in data["items"]:
        assert 12 <= item["price"] <= 15 