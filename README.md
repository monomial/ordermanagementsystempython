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
4. Run the application:
   ```
   uvicorn app.main:app --reload
   ```
   or
   ```
   python run.py
   ```
5. Access the API documentation at http://localhost:8000/docs

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