from tortoise import Tortoise, fields
from tortoise.models import Model
from tortoise import run_async
from tortoise.transactions import in_transaction

# SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./order_management.db"

# Dependency to get DB session
async def init():
    await Tortoise.init(
        db_url=SQLALCHEMY_DATABASE_URL,
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
