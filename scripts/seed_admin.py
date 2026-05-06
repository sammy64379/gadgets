import os
import sys

# ensure project root is on sys.path so imports work regardless of how script is run
# adding the parent directory of this file (the project root) to the front of sys.path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root not in sys.path:
    sys.path.insert(0, root)

from getpass import getpass

from dotenv import load_dotenv

from app import app
from app.db_models import db, User
from werkzeug.security import generate_password_hash

# load any environment variables just in case
load_dotenv()


def create_admin():
    """Interactive helper to create or mark the first administrator.

    Run this from the project root. You can invoke it either directly or as a module:

        # direct (adds scripts/ to sys.path automatically)
        python scripts/seed_admin.py

        # module-style (makes project root available for imports)
        python -m scripts.seed_admin

    The script also modifies sys.path at startup so that `import app` works even if
    Python adds the `scripts` directory to the path instead of the project root.

    If a user with the supplied email already exists the script will simply
    flip the ``admin`` flag on; otherwise it will prompt for a name and
    password and insert a new record.
    """

    with app.app_context():
        email = input("Admin email: ").strip()
        if not email:
            print("email is required")
            return

        existing = User.query.filter_by(email=email).first()
        if existing:
            if existing.admin:
                print(f"{email} is already an administrator")
            else:
                existing.admin = True
                db.session.commit()
                print(f"{email} has been promoted to admin")
            return

        name = (
            input("Name (leave blank for 'Administrator'): ").strip() or "Administrator"
        )
        password = getpass("Password: ")
        confirm = getpass("Confirm password: ")
        if password != confirm:
            print("Passwords do not match, aborting")
            return

        hashed = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
        user = User(
            name=name,
            email=email,
            password=hashed,
            phone="",
            admin=True,
            email_confirmed=True,
        )
        db.session.add(user)
        db.session.commit()
        print(f"Created admin user {email}")


if __name__ == "__main__":
    create_admin()
