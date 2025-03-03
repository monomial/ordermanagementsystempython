from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import datetime

from app.api.routes import customers, products, orders, inventory
from app.api.routes.v2 import products as products_v2
from app.db.database import init, close

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code here
    await init()  # Initialize Tortoise ORM
    yield
    # Shutdown code here
    await close()  # Close Tortoise ORM connections

app = FastAPI(
    title="Order Management System",
    description="A simple API for managing orders, customers, products, and inventory",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API version prefixes
API_V1_PREFIX = "/api/v1"
API_V2_PREFIX = "/api/v2"

# Include v1 routers
app.include_router(customers.router, prefix=f"{API_V1_PREFIX}/customers", tags=["customers"])
app.include_router(products.router, prefix=f"{API_V1_PREFIX}/products", tags=["products"])
app.include_router(orders.router, prefix=f"{API_V1_PREFIX}/orders", tags=["orders"])
app.include_router(inventory.router, prefix=f"{API_V1_PREFIX}/inventory", tags=["inventory"])

# Include v2 routers
app.include_router(products_v2.router, prefix=f"{API_V2_PREFIX}/products", tags=["products-v2"])

@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Welcome to the Order Management System API",
        "docs": "/docs",
        "endpoints": {
            "v1": [
                f"{API_V1_PREFIX}/customers",
                f"{API_V1_PREFIX}/products",
                f"{API_V1_PREFIX}/orders",
                f"{API_V1_PREFIX}/inventory"
            ],
            "v2": [
                f"{API_V2_PREFIX}/products"
            ]
        },
        "versions": ["v1", "v2"]
    } 