"""
Database service for Kosvio authentication.

Supports connection to Google Cloud SQL for MySQL in production, and falls
back to a local SQLite database for local development if MySQL variables are not configured.
"""

import os
import re
import hashlib
import logging
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Tuple
import pymysql
import pymysql.cursors

# Setup local logger
logger = logging.getLogger(__name__)

# Fallback SQLite DB path
SQLITE_DB_PATH = Path(__file__).resolve().parent / "auth_db.sqlite"


def is_mysql_configured() -> bool:
    """Check if MySQL/Cloud SQL connection environment variables are set."""
    return bool(os.getenv("MYSQL_HOST") or os.getenv("MYSQL_UNIX_SOCKET"))


def get_db_type() -> str:
    """Return the database type to use (mysql or sqlite)."""
    return "mysql" if is_mysql_configured() else "sqlite"


def get_connection():
    """
    Establish a connection to either MySQL or local SQLite, depending on configuration.
    """
    if get_db_type() == "mysql":
        db_host = os.getenv("MYSQL_HOST")
        db_port = int(os.getenv("MYSQL_PORT", "3306"))
        db_user = os.getenv("MYSQL_USER")
        db_password = os.getenv("MYSQL_PASSWORD")
        db_name = os.getenv("MYSQL_DB")
        db_socket = os.getenv("MYSQL_UNIX_SOCKET")

        if db_socket:
            logger.info(f"Connecting to MySQL via Unix socket: {db_socket}")
            return pymysql.connect(
                unix_socket=db_socket,
                user=db_user,
                password=db_password,
                database=db_name,
                cursorclass=pymysql.cursors.DictCursor
            )
        else:
            logger.info(f"Connecting to MySQL via TCP: {db_host}:{db_port}")
            return pymysql.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                database=db_name,
                cursorclass=pymysql.cursors.DictCursor
            )
    else:
        logger.info(f"No MySQL configuration found. Using local SQLite database at: {SQLITE_DB_PATH}")
        conn = sqlite3.connect(str(SQLITE_DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn


def init_db() -> None:
    """Initialize the database tables if they do not exist."""
    db_type = get_db_type()
    conn = get_connection()
    try:
        cursor = conn.cursor()
        try:
            if db_type == "mysql":
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            else:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        name TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
        finally:
            cursor.close()
        conn.commit()
        logger.info(f"Database ({db_type}) initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database ({db_type}): {str(e)}", exc_info=True)
        raise e
    finally:
        conn.close()


def hash_password(password: str) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with a unique salt."""
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return salt.hex() + ":" + key.hex()


def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a password against its stored hash."""
    try:
        salt_hex, key_hex = stored_password.split(":")
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)
        new_key = hashlib.pbkdf2_hmac(
            "sha256", provided_password.encode("utf-8"), salt, 100000
        )
        return key == new_key
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """Validate email format using standard regex."""
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(email_regex, email.strip()))


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password strength requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character (e.g. !@#$%^&*)."
    return True, "Strong password."


def create_user(email: str, password: str, name: str) -> Tuple[bool, str]:
    """
    Register a new user in the system with validations.

    Returns:
        (bool, str): (Success state, message/error details).
    """
    init_db()  # Ensure DB is ready
    email_clean = email.strip().lower()
    name_clean = name.strip()

    if not email_clean or not password or not name_clean:
        return False, "All fields are required."

    if not validate_email(email_clean):
        return False, "Invalid email address format."

    is_strong, strength_msg = validate_password_strength(password)
    if not is_strong:
        return False, strength_msg

    pw_hash = hash_password(password)

    db_type = get_db_type()
    query = (
        "INSERT INTO users (email, password_hash, name) VALUES (%s, %s, %s)"
        if db_type == "mysql"
        else "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)"
    )

    conn = get_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute(query, (email_clean, pw_hash, name_clean))
        finally:
            cursor.close()
        conn.commit()
        return True, "Account created successfully."
    except (pymysql.IntegrityError, sqlite3.IntegrityError):
        return False, "An account with this email already exists."
    except Exception as e:
        logger.error("Failed to create user in database: %s", str(e), exc_info=True)
        return False, "An unexpected database error occurred. Please try again later."
    finally:
        conn.close()


def verify_user(email: str, password: str) -> Optional[Dict]:
    """
    Verify user credentials.

    Returns:
        Optional[Dict]: Dict containing user info (email, name) if successful, None otherwise.
    """
    init_db()  # Ensure DB is ready
    email_clean = email.strip().lower()

    if not email_clean or not password:
        return None

    db_type = get_db_type()
    query = (
        "SELECT email, password_hash, name FROM users WHERE email = %s"
        if db_type == "mysql"
        else "SELECT email, password_hash, name FROM users WHERE email = ?"
    )

    conn = get_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute(query, (email_clean,))
            row = cursor.fetchone()

            if row and verify_password(row["password_hash"], password):
                return {"email": row["email"], "name": row["name"]}
        finally:
            cursor.close()
    except Exception as e:
        logger.error("Failed to verify user credentials: %s", str(e), exc_info=True)
    finally:
        conn.close()
    return None
