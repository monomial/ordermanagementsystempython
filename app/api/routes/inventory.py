from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime

from app.models.models import Inventory, Product
from app.schemas.schemas import InventoryCreate, Inventory as InventorySchema, InventoryUpdate

router = APIRouter()

@router.post("/", response_model=InventorySchema, status_code=status.HTTP_201_CREATED)
async def create_inventory(inventory: InventoryCreate):
    # Check if product exists
    product = await Product.filter(id=inventory.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if inventory for this product already exists
    existing_inventory = await Inventory.filter(product_id=inventory.product_id).first()
    if existing_inventory:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inventory for this product already exists"
        )
    
    # Create new inventory
    db_inventory = await Inventory.create(**inventory.dict())
    return db_inventory

@router.get("/", response_model=List[InventorySchema])
async def read_inventories(skip: int = 0, limit: int = 100):
    inventories = await Inventory.all().offset(skip).limit(limit)
    return inventories

@router.get("/{inventory_id}", response_model=InventorySchema)
async def read_inventory(inventory_id: int):
    db_inventory = await Inventory.filter(id=inventory_id).first()
    if db_inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found"
        )
    return db_inventory

@router.get("/product/{product_id}", response_model=InventorySchema)
async def read_inventory_by_product(product_id: int):
    db_inventory = await Inventory.filter(product_id=product_id).first()
    if db_inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory for this product not found"
        )
    return db_inventory

@router.put("/{inventory_id}", response_model=InventorySchema)
async def update_inventory(inventory_id: int, inventory: InventoryUpdate):
    db_inventory = await Inventory.filter(id=inventory_id).first()
    if db_inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found"
        )
    
    # Update inventory fields
    update_data = inventory.dict(exclude_unset=True)
    
    # If quantity is being updated, update last_restock_date
    if "quantity" in update_data and update_data["quantity"] > db_inventory.quantity:
        update_data["last_restock_date"] = datetime.now(datetime.UTC)
    
    for key, value in update_data.items():
        setattr(db_inventory, key, value)
    
    await db_inventory.save()
    return db_inventory

@router.delete("/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory(inventory_id: int):
    db_inventory = await Inventory.filter(id=inventory_id).first()
    if db_inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found"
        )
    
    await db_inventory.delete()
    return None 