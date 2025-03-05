# Order Management System

A simple backend web application for managing orders, built with FastAPI and SQLite.

## Features

- Customer management
- Product management
- Order creation and tracking
- Basic inventory management
- RESTful API endpoints with versioning (v1 and v2)

## Setup and Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Initialize the database:
   ```
   python scripts/init_aerich.py
   ```
5. Run the application:
   ```
   uvicorn app.main:app --reload
   ```
   or
   ```
   python run.py
   ```
6. Access the API documentation at http://localhost:8001/docs

## Database Management

The application uses SQLite as the database and Tortoise ORM for data access. The database file is created at `./order_management.db`.

### Database Scripts

The `scripts` directory contains utilities for managing the database:

1. **Seed Database**: Populate the database with sample data
   ```
   python scripts/seed_data.py
   ```

2. **View Database**: Display the current contents of the database in a formatted table view
   ```
   python scripts/view_database.py
   ```

3. **Run Migrations**: Manage database schema changes
   ```
   python scripts/run_migrations.py --help
   ```

For more information about these scripts, see the [scripts/README.md](scripts/README.md) file.

### Database Migrations

This project uses Aerich for database migrations with Tortoise ORM. To create and apply migrations:

1. Initialize Aerich (if not already done):
   ```
   python scripts/run_migrations.py init
   python scripts/run_migrations.py init-db
   ```

2. Create a new migration after changing models:
   ```
   python scripts/run_migrations.py migrate --name "Description of changes"
   ```

3. Apply migrations:
   ```
   python scripts/run_migrations.py upgrade
   ```

4. View migration history:
   ```
   python scripts/run_migrations.py history
   ```

## API Endpoints

### v1 API

Basic CRUD operations:

- `/api/v1/customers` - Customer management
- `/api/v1/products` - Product management
- `/api/v1/orders` - Order management
- `/api/v1/inventory` - Inventory management

### v2 API

Enhanced endpoints with additional features:

- `/api/v2/products` - Product management with pagination and filtering
  - Supports pagination parameters: `page` and `page_size`
  - Supports filtering by: `name`, `min_price`, and `max_price`
  - Returns metadata: total items, total pages, next/previous page indicators

## Testing

Run tests with:
```
pytest
```

## License

MIT
