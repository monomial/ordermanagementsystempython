from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.database import get_db
from app.models.models import Inventory, Product
from app.schemas.schemas import InventoryCreate, Inventory as InventorySchema, InventoryUpdate

router = APIRouter()

@router.post("/", response_model=InventorySchema, status_code=status.HTTP_201_CREATED)
def create_inventory(inventory: InventoryCreate, db: Session = Depends(get_db)):
    # Check if product exists
    product = db.query(Product).filter(Product.id == inventory.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if inventory for this product already exists
    existing_inventory = db.query(Inventory).filter(Inventory.product_id == inventory.product_id).first()
    if existing_inventory:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inventory for this product already exists"
        )
    
    # Create new inventory
    db_inventory = Inventory(**inventory.dict())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

@router.get("/", response_model=List[InventorySchema])
def read_inventories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    inventories = db.query(Inventory).offset(skip).limit(limit).all()
    return inventories

@router.get("/{inventory_id}", response_model=InventorySchema)
def read_inventory(inventory_id: int, db: Session = Depends(get_db)):
    db_inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if db_inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found"
        )
    return db_inventory

@router.get("/product/{product_id}", response_model=InventorySchema)
def read_inventory_by_product(product_id: int, db: Session = Depends(get_db)):
    db_inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if db_inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory for this product not found"
        )
    return db_inventory

@router.put("/{inventory_id}", response_model=InventorySchema)
def update_inventory(inventory_id: int, inventory: InventoryUpdate, db: Session = Depends(get_db)):
    db_inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if db_inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found"
        )
    
    # Update inventory fields
    update_data = inventory.dict(exclude_unset=True)
    
    # If quantity is being updated, update last_restock_date
    if "quantity" in update_data and update_data["quantity"] > db_inventory.quantity:
        update_data["last_restock_date"] = datetime.utcnow()
    
    for key, value in update_data.items():
        setattr(db_inventory, key, value)
    
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

@router.delete("/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory(inventory_id: int, db: Session = Depends(get_db)):
    db_inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if db_inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found"
        )
    
    db.delete(db_inventory)
    db.commit()
    return None 