from fastapi import APIRouter, HTTPException, status
from typing import List

from app.models.models import Product
from app.schemas.schemas import ProductCreate, Product as ProductSchema, ProductUpdate

router = APIRouter()

@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate):
    # Check if product with SKU already exists
    db_product = await Product.filter(sku=product.sku).first()
    if db_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this SKU already exists"
        )
    
    # Create new product
    db_product = await Product.create(**product.dict())
    return db_product

@router.get("/", response_model=List[ProductSchema])
async def read_products(skip: int = 0, limit: int = 100):
    products = await Product.all().offset(skip).limit(limit)
    return products

@router.get("/{product_id}", response_model=ProductSchema)
async def read_product(product_id: int):
    db_product = await Product.filter(id=product_id).first()
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return db_product

@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(product_id: int, product: ProductUpdate):
    db_product = await Product.filter(id=product_id).first()
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if updating SKU and if it already exists
    if product.sku is not None and product.sku != db_product.sku:
        existing_product = await Product.filter(sku=product.sku).first()
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this SKU already exists"
            )
    
    # Update product fields
    update_data = product.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    await db_product.save()
    return db_product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int):
    db_product = await Product.filter(id=product_id).first()
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    await db_product.delete()
    return None 