from tortoise import Tortoise, fields
from tortoise.models import Model
from tortoise import run_async
from tortoise.transactions import in_transaction
import os

# Get the absolute path to the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# SQLite database URL with absolute path
DATABASE_URL = f"sqlite://{os.path.join(BASE_DIR, 'order_management.db')}"
# Keep the old name for backward compatibility with existing code
SQLALCHEMY_DATABASE_URL = DATABASE_URL

# Dependency to get DB session
async def init():
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={"models": ["app.models.models"]}
    )
    await Tortoise.generate_schemas()

async def close():
    await Tortoise.close_connections()

async def get_db():
    async with in_transaction() as db:
        yield db

# Optional: Pydantic configuration for models (if needed elsewhere)
model_config = {
    "from_attributes": True
}

# Run the initialization
if __name__ == "__main__":
    run_async(init())
