"""
Backwards-compatibility bridge.
All database connection and configuration logic is centralized in connection.py.
"""

from connection import (
    get_connection,
    get_cursor,
    test_connection,
    hash_password,
    verify_password,
    init_db,
    DB_CONFIG,
    DB_HOST,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
)

__all__ = [
    "get_connection",
    "get_cursor",
    "test_connection",
    "hash_password",
    "verify_password",
    "init_db",
    "DB_CONFIG",
    "DB_HOST",
    "DB_USER",
    "DB_PASSWORD",
    "DB_NAME",
]
