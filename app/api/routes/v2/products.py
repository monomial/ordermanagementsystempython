from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from math import ceil

from app.db.database import get_db
from app.models.models import Product
from app.schemas.schemas import Product as ProductSchema
from app.schemas.v2.schemas import PaginatedResponse

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[ProductSchema])
def read_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    name: Optional[str] = Query(None, description="Filter products by name"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of products with optional filtering.
    
    - **page**: Page number (starts at 1)
    - **page_size**: Number of items per page (default: 10, max: 100)
    - **name**: Optional filter by product name (case-insensitive partial match)
    - **min_price**: Optional filter for minimum price
    - **max_price**: Optional filter for maximum price
    """
    # Start with base query
    query = db.query(Product)
    
    # Apply filters if provided
    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # Get total count for pagination
    total_items = query.count()
    total_pages = ceil(total_items / page_size)
    
    # Apply pagination
    products = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # Prepare response with pagination metadata
    return {
        "items": products,
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }

@router.get("/{product_id}", response_model=ProductSchema)
def read_product(product_id: int, db: Session = Depends(get_db)):
    """
    Get a specific product by ID.
    """
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return db_product 