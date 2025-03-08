# Order Management System - Developer Guide

## Introduction

Welcome to the Order Management System! This guide is designed for developers who are familiar with Python but new to FastAPI, Tortoise ORM, and Aerich. This document will help you understand the project structure, the technologies used, and how to get started with development.

## Technologies Used

- **FastAPI**: A modern, fast web framework for building APIs with Python 3.7+
- **Tortoise ORM**: An easy-to-use async ORM (Object Relational Mapper) inspired by Django
- **Aerich**: A database migration tool for Tortoise ORM
- **Pydantic**: Data validation and settings management using Python type annotations
- **SQLite**: A lightweight disk-based database (used in this project, but can be replaced)
- **Uvicorn**: ASGI server for running FastAPI applications

## Project Structure

```
order_management_system/
├── app/                        # Main application package
│   ├── api/                    # API endpoints
│   │   ├── routes/             # Route definitions
│   │   │   ├── customers.py    # Customer endpoints
│   │   │   ├── products.py     # Product endpoints
│   │   │   ├── orders.py       # Order endpoints
│   │   │   ├── inventory.py    # Inventory endpoints
│   │   │   └── v2/             # API version 2 endpoints
│   ├── db/                     # Database configuration
│   │   └── database.py         # Database connection setup
│   ├── models/                 # Data models
│   │   └── models.py           # Tortoise ORM models
│   ├── schemas/                # Pydantic schemas
│   │   └── schemas.py          # Request/response schemas
│   └── main.py                 # Application entry point
├── migrations/                 # Database migrations
├── tests/                      # Test cases
├── scripts/                    # Utility scripts
├── aerich.ini                  # Aerich configuration
├── requirements.txt            # Project dependencies
├── run.py                      # Script to run the application
└── order_management.db         # SQLite database file
```

## Core Concepts

### 1. FastAPI Basics

FastAPI is a modern, fast web framework for building APIs with Python. It's built on top of Starlette for the web parts and Pydantic for the data parts.

Key features:
- **Fast**: Very high performance, on par with NodeJS and Go
- **Easy**: Designed to be easy to use and learn
- **Automatic docs**: Interactive API documentation with Swagger UI and ReDoc
- **Type hints**: Leverages Python type hints for validation, serialization, and documentation

In our project, the FastAPI application is initialized in `app/main.py` and routes are defined in the `app/api/routes/` directory.

### 2. Tortoise ORM

Tortoise ORM is an async ORM inspired by Django ORM. It's designed to be easy to use and to work well with async Python code.

Key concepts:
- **Models**: Python classes that represent database tables
- **Fields**: Attributes of models that map to database columns
- **Relationships**: Connections between models (ForeignKey, OneToOne, ManyToMany)
- **QuerySet**: API for querying the database

In our project, models are defined in `app/models/models.py`.

### 3. Aerich

Aerich is a database migration tool for Tortoise ORM, similar to Alembic for SQLAlchemy. It helps manage database schema changes over time.

Key commands:
- `aerich init-db`: Initialize the database with the current models
- `aerich migrate`: Generate a migration file based on model changes
- `aerich upgrade`: Apply migrations to the database

The Aerich configuration is in `aerich.ini`.

## Data Models

Our application has the following main models:

### Customer
Represents a customer who can place orders.
- Fields: id, name, email, phone, address, notes, created_at, updated_at
- Relationships: has many Orders

### Product
Represents a product that can be ordered.
- Fields: id, name, description, price, sku, created_at, updated_at
- Relationships: has one Inventory, has many OrderItems

### Order
Represents an order placed by a customer.
- Fields: id, customer_id, order_date, status, total_amount, created_at, updated_at
- Relationships: belongs to Customer, has many OrderItems

### OrderItem
Represents an item in an order.
- Fields: id, order_id, product_id, quantity, unit_price, subtotal, created_at, updated_at
- Relationships: belongs to Order, belongs to Product

### Inventory
Represents the inventory of a product.
- Fields: id, product_id, quantity, last_restock_date, created_at, updated_at
- Relationships: belongs to Product

## API Endpoints

The API is organized into the following endpoints:

### Customers API
- `GET /api/v1/customers`: List all customers
- `POST /api/v1/customers`: Create a new customer
- `GET /api/v1/customers/{id}`: Get a specific customer
- `PUT /api/v1/customers/{id}`: Update a customer
- `DELETE /api/v1/customers/{id}`: Delete a customer

### Products API
- `GET /api/v1/products`: List all products
- `POST /api/v1/products`: Create a new product
- `GET /api/v1/products/{id}`: Get a specific product
- `PUT /api/v1/products/{id}`: Update a product
- `DELETE /api/v1/products/{id}`: Delete a product

### Orders API
- `GET /api/v1/orders`: List all orders
- `POST /api/v1/orders`: Create a new order
- `GET /api/v1/orders/{id}`: Get a specific order
- `PUT /api/v1/orders/{id}`: Update an order
- `DELETE /api/v1/orders/{id}`: Delete an order
- `GET /api/v1/orders/{id}/items`: Get items in an order

### Inventory API
- `GET /api/v1/inventory`: List all inventory
- `POST /api/v1/inventory`: Create a new inventory record
- `GET /api/v1/inventory/{id}`: Get a specific inventory record
- `PUT /api/v1/inventory/{id}`: Update an inventory record
- `DELETE /api/v1/inventory/{id}`: Delete an inventory record

## Getting Started

### Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd order-management-system
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python run.py
   ```

5. Access the API documentation:
   - Swagger UI: http://localhost:8001/docs
   - ReDoc: http://localhost:8001/redoc

### Database Migrations

To create and apply database migrations:

1. Initialize the database (first time only):
   ```bash
   aerich init-db
   ```

2. After making changes to models, create a migration:
   ```bash
   aerich migrate --name "describe_your_changes"
   ```

3. Apply the migration:
   ```bash
   aerich upgrade
   ```

## Working with Tortoise ORM

### Creating Records

```python
# Create a customer
customer = await Customer.create(
    name="John Doe",
    email="john@example.com",
    phone="123-456-7890"
)

# Create a product
product = await Product.create(
    name="Widget",
    description="A fantastic widget",
    price=19.99,
    sku="WDG-001"
)

# Create inventory for the product
inventory = await Inventory.create(
    product=product,
    quantity=100
)
```

### Querying Records

```python
# Get all customers
customers = await Customer.all()

# Get a specific customer
customer = await Customer.filter(id=1).first()

# Get customers with filtering
premium_customers = await Customer.filter(
    orders__total_amount__gte=1000
).distinct()

# Get related records
customer_orders = await customer.orders.all()
```

### Updating Records

```python
# Update a customer
customer = await Customer.filter(id=1).first()
customer.name = "Jane Doe"
await customer.save()

# Bulk update
await Customer.filter(address__contains="New York").update(region="East")
```

### Deleting Records

```python
# Delete a customer
customer = await Customer.filter(id=1).first()
await customer.delete()

# Bulk delete
await Customer.filter(last_order__lt=one_year_ago).delete()
```

## Transactions

Tortoise ORM supports transactions to ensure data consistency:

```python
from tortoise import transactions

async with transactions.in_transaction():
    # All database operations here will be in a transaction
    customer = await Customer.create(name="John", email="john@example.com")
    product = await Product.filter(id=1).first()
    # If any operation fails, the transaction will be rolled back
```

## Testing

The project includes a test suite using pytest. To run the tests:

```bash
pytest
```

## Common Tasks

### Adding a New Endpoint

1. Define a new route in the appropriate file in `app/api/routes/`
2. If needed, add new schemas in `app/schemas/schemas.py`
3. Implement the endpoint logic using Tortoise ORM

Example:
```python
@router.get("/top-customers", response_model=List[CustomerSchema])
async def get_top_customers(limit: int = 10):
    customers = await Customer.filter(
        orders__isnull=False
    ).annotate(
        order_count=Count('orders')
    ).order_by('-order_count').limit(limit)
    return customers
```

### Adding a New Model

1. Define the model in `app/models/models.py`
2. Create corresponding schemas in `app/schemas/schemas.py`
3. Create a migration using Aerich
4. Implement API endpoints for the new model

## Troubleshooting

### Common Issues

1. **Database connection errors**:
   - Check that the database file exists and has the correct permissions
   - Verify the database URL in `app/db/database.py`

2. **Migration errors**:
   - Make sure all model changes are properly defined
   - Try running `aerich migrate --name "fix"` to generate a new migration

3. **API errors**:
   - Check the FastAPI logs for detailed error messages
   - Verify that the request body matches the expected schema

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Tortoise ORM Documentation](https://tortoise-orm.readthedocs.io/)
- [Aerich Documentation](https://github.com/tortoise/aerich)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)

## Contributing

1. Create a new branch for your feature or bugfix
2. Write tests for your changes
3. Implement your changes
4. Run the tests to make sure everything works
5. Submit a pull request

Happy coding! 