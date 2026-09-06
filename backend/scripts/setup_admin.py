"""CLI utility to create or promote dedicated administrator accounts."""
import argparse
import getpass
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from src.infrastructure.db.session import get_session_factory
from src.infrastructure.db.repositories.pg_user_repository import PgUserRepository
from src.infrastructure.security.password import hash_password
from src.domain.entities.user import User


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or manage administrator accounts.")
    parser.add_argument("--create", action="store_true", help="Create a fresh administrator account interactively.")
    parser.add_argument("--email", type=str, help="Email of an existing user to promote.")
    parser.add_argument("--promote", action="store_true", help="Promote the specified user to admin.")
    args = parser.parse_args()

    # Open direct standalone session outside Flask request context
    session_factory = get_session_factory()
    session = session_factory()
    user_repo = PgUserRepository(session)

    try:
        if args.create:
            print("=== Create Dedicated Administrator Account ===")
            email = input("Enter Admin Email: ").strip().lower()
            if not email or "@" not in email:
                print("Error: A valid email address is required.")
                sys.exit(1)

            existing = user_repo.get_by_email(email)
            if existing:
                print(f"Error: An account with email '{email}' already exists. Use --email {email} --promote instead.")
                sys.exit(1)

            full_name = input("Enter Admin Full Name: ").strip() or "System Administrator"
            pwd = getpass.getpass("Enter Admin Password: ")
            pwd_confirm = getpass.getpass("Confirm Admin Password: ")

            if pwd != pwd_confirm:
                print("Error: Passwords do not match.")
                sys.exit(1)

            if len(pwd) < 8:
                print("Error: Password must be at least 8 characters long.")
                sys.exit(1)

            user = User(
                email=email,
                password_hash=hash_password(pwd),
                full_name=full_name,
                role="admin",
            )
            user_repo.save(user)
            session.commit()
            print(f"[SUCCESS] Dedicated administrator account '{email}' created successfully!")
            return

        if args.promote and args.email:
            user = user_repo.get_by_email(args.email.strip().lower())
            if not user:
                print(f"Error: User with email '{args.email}' not found.")
                sys.exit(1)
            user.role = "admin"
            user_repo.save(user)
            session.commit()
            print(f"[SUCCESS] User '{args.email}' has been promoted to administrator.")
            return

        parser.print_help()
    finally:
        session.close()


if __name__ == "__main__":
    main()