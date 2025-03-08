#!/usr/bin/env python3
"""
Script to run database migrations using Aerich for Tortoise ORM.
"""
import sys
import os
import argparse
import asyncio

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aerich import Command
from app.db.database import DATABASE_URL

# Convert URL to Tortoise format if needed
# sqlite:///./order_management.db -> sqlite://order_management.db
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

async def run_migrations(args):
    """Run database migrations based on the provided arguments."""
    command = Command(tortoise_config=TORTOISE_ORM, app="models")
    
    # Determine which command to run
    if args.command == 'init':
        print("Initializing Aerich...")
        await command.init()
    
    elif args.command == 'init-db':
        print("Initializing database...")
        await command.init_db(safe=True)
    
    elif args.command == 'migrate':
        if args.name:
            print(f"Creating a new migration with name: {args.name}...")
            await command.migrate(args.name)
        else:
            print("Error: A name is required for the 'migrate' command.")
            sys.exit(1)
    
    elif args.command == 'upgrade':
        print("Upgrading database to the latest version...")
        await command.upgrade()
    
    elif args.command == 'downgrade':
        if args.version:
            print(f"Downgrading database to version {args.version}...")
            await command.downgrade(args.version)
        else:
            print("Error: A version is required for the 'downgrade' command.")
            sys.exit(1)
    
    elif args.command == 'history':
        print("Showing migration history...")
        migrations = await command.history()
        for migration in migrations:
            print(f"Version: {migration.version}")
            print(f"App: {migration.app}")
            print(f"Name: {migration.name}")
            print(f"Applied: {migration.applied}")
            print("-" * 50)
    
    elif args.command == 'heads':
        print("Showing current heads...")
        heads = await command.heads()
        for head in heads:
            print(f"App: {head[0]}, Version: {head[1]}")
    
    else:
        print(f"Error: Unknown command '{args.command}'")
        sys.exit(1)
    
    print("Done!")

def main():
    parser = argparse.ArgumentParser(description='Run database migrations with Aerich.')
    subparsers = parser.add_subparsers(dest='command', help='Migration command to run')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize Aerich for the project')
    
    # Init-db command
    init_db_parser = subparsers.add_parser('init-db', help='Initialize the database')
    
    # Migrate command
    migrate_parser = subparsers.add_parser('migrate', help='Create a new migration')
    migrate_parser.add_argument('--name', '-n', required=True, help='Name for the migration')
    
    # Upgrade command
    upgrade_parser = subparsers.add_parser('upgrade', help='Upgrade the database to the latest version')
    
    # Downgrade command
    downgrade_parser = subparsers.add_parser('downgrade', help='Revert the database to a previous version')
    downgrade_parser.add_argument('--version', '-v', required=True, help='Version to downgrade to')
    
    # History command
    history_parser = subparsers.add_parser('history', help='Show migration history')
    
    # Heads command
    heads_parser = subparsers.add_parser('heads', help='Show current migration heads')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    asyncio.run(run_migrations(args))

if __name__ == "__main__":
    main()
