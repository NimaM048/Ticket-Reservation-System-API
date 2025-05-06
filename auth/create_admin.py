import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import SessionLocal
from database.models import DbUsers
from passlib.hash import bcrypt

db = SessionLocal()

def create_admin():
    username = "nima"
    password = "1234"
    hashed_password = bcrypt.hash(password)
    email = "admin@example.com"

    admin_user = DbUsers(
        username=username,
        password=hashed_password,
        email=email,
        is_admin=True
    )

    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    print(f"Admin user {admin_user.username} created successfully!")

if __name__ == "__main__":
    create_admin()
