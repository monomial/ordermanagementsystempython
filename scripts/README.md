# Database Scripts

This directory contains scripts for managing the database in the Order Management System.

## Setup

Before running these scripts, make sure you have installed all the required dependencies:

```bash
pip install -r ../requirements.txt
```

## Available Scripts

### 1. Seed Database

The `seed_data.py` script populates the database with sample data for testing and development purposes.

```bash
python seed_data.py
```

This script will:
- Clear any existing data in the database
- Create sample customers, products, inventory records, and orders
- Generate realistic relationships between these entities

### 2. View Database

The `view_database.py` script displays the current contents of the database in a formatted table view.

```bash
python view_database.py
```

This script will show:
- Customers
- Products
- Inventory levels
- Orders
- Order details (products in each order)

## Database Migrations

This project uses Alembic for database migrations. The migration files are stored in the `../migrations` directory.

You can use the `run_migrations.py` script to manage database migrations:

### Creating a New Migration

To create a new migration after changing the database models:

```bash
python run_migrations.py revision -m "Description of changes" -a
```

The `-a` flag enables autogeneration based on model changes.

### Applying Migrations

To apply all pending migrations:

```bash
python run_migrations.py upgrade
```

To apply migrations up to a specific version:

```bash
python run_migrations.py upgrade <revision_id>
```

### Downgrading Migrations

To downgrade to a previous version:

```bash
python run_migrations.py downgrade <revision_id>
```

### Migration History

To see the migration history:

```bash
python run_migrations.py history
```

### Current Migration

To see the current migration version:

```bash
python run_migrations.py current
```

### Help

For more information on available commands:

```bash
python run_migrations.py --help
```

## Database Schema

The database schema includes the following tables:

- `customers`: Stores customer information
- `products`: Stores product information
- `inventory`: Tracks inventory levels for each product
- `orders`: Stores order information
- `order_products`: Association table for the many-to-many relationship between orders and products

For more details on the schema, refer to the models defined in `../app/models/models.py`.
