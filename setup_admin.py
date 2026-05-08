"""
Run this once locally to generate your admin password hash.

Usage:
    python setup_admin.py

Paste the printed hash into .streamlit/secrets.toml as ADMIN_PASSWORD_HASH.
"""
import bcrypt
import getpass

password = getpass.getpass("Choose an admin password: ")
confirm = getpass.getpass("Confirm password: ")

if password != confirm:
    print("Passwords do not match.")
else:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()
    print("\nAdd this line to .streamlit/secrets.toml:\n")
    print(f'ADMIN_PASSWORD_HASH = "{hashed}"')
    print()
