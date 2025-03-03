#!/usr/bin/env python3
"""
Script to run database migrations.
"""
import sys
import os
import argparse
from alembic.config import Config
from alembic import command

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_migrations(args):
    """Run database migrations based on the provided arguments."""
    # Get the path to the alembic.ini file
    alembic_ini = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'alembic.ini')
    
    # Create the Alembic configuration
    alembic_cfg = Config(alembic_ini)
    
    # Determine which command to run
    if args.command == 'upgrade':
        if args.revision == 'head':
            print("Upgrading database to the latest revision...")
            command.upgrade(alembic_cfg, 'head')
        else:
            print(f"Upgrading database to revision {args.revision}...")
            command.upgrade(alembic_cfg, args.revision)
    elif args.command == 'downgrade':
        if args.revision == 'base':
            print("Downgrading database to the base revision...")
            command.downgrade(alembic_cfg, 'base')
        else:
            print(f"Downgrading database to revision {args.revision}...")
            command.downgrade(alembic_cfg, args.revision)
    elif args.command == 'revision':
        if args.message:
            if args.autogenerate:
                print(f"Creating a new revision with message: {args.message} (autogenerate)...")
                command.revision(alembic_cfg, message=args.message, autogenerate=True)
            else:
                print(f"Creating a new revision with message: {args.message}...")
                command.revision(alembic_cfg, message=args.message, autogenerate=False)
        else:
            print("Error: A message is required for the 'revision' command.")
            sys.exit(1)
    elif args.command == 'history':
        print("Showing migration history...")
        command.history(alembic_cfg)
    elif args.command == 'current':
        print("Showing current revision...")
        command.current(alembic_cfg)
    else:
        print(f"Error: Unknown command '{args.command}'")
        sys.exit(1)
    
    print("Done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run database migrations.')
    subparsers = parser.add_subparsers(dest='command', help='Migration command to run')
    
    # Upgrade command
    upgrade_parser = subparsers.add_parser('upgrade', help='Upgrade the database to a later version')
    upgrade_parser.add_argument('revision', nargs='?', default='head', help='Revision to upgrade to (default: head)')
    
    # Downgrade command
    downgrade_parser = subparsers.add_parser('downgrade', help='Revert the database to a previous version')
    downgrade_parser.add_argument('revision', help='Revision to downgrade to')
    
    # Revision command
    revision_parser = subparsers.add_parser('revision', help='Create a new revision')
    revision_parser.add_argument('--message', '-m', required=True, help='Message for the revision')
    revision_parser.add_argument('--autogenerate', '-a', action='store_true', help='Autogenerate the revision based on model changes')
    
    # History command
    history_parser = subparsers.add_parser('history', help='Show migration history')
    
    # Current command
    current_parser = subparsers.add_parser('current', help='Show current revision')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    run_migrations(args)
