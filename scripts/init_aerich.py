#!/usr/bin/env python3
"""
Script to initialize Aerich for the project.
"""
import sys
import os
import asyncio

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aerich import Command
from app.db.database import DATABASE_URL

# Convert URL to Tortoise format if needed
DB_URL = DATABASE_URL.replace('sqlite:///./','sqlite://')

# Tortoise ORM config
TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {
            "models": ["app.models.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

async def init():
    """Initialize Aerich."""
    command = Command(tortoise_config=TORTOISE_ORM, app="models")
    
    # Initialize Aerich
    await command.init()
    
    # Initialize the database
    await command.init_db(create_db=True)
    
    print("Aerich initialized successfully!")

if __name__ == "__main__":
    asyncio.run(init()) 