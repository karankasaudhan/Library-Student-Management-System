import mysql.connector as s
import os
from connection import get_connection, hash_password, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_NAME

connection = None
cursor = None

try:
    connection = get_connection(use_database=False)
    cursor = connection.cursor()

    db_name = os.getenv("DB_NAME", "library")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
    cursor.execute(f"USE `{db_name}`")
    print(f"Database '{db_name}' ready.")

    # 1. BOOK TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS book (
            SRNO INT NOT NULL AUTO_INCREMENT,
            BOOK_NAME VARCHAR(100) NOT NULL,
            Class VARCHAR(20) NOT NULL,
            quantity INT NOT NULL DEFAULT 0,
            STATUS VARCHAR(10) DEFAULT 'ACTIVE',
            PRIMARY KEY (SRNO),
            UNIQUE KEY (BOOK_NAME)
        )
    """)

    # 2. STUDENT TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student (
            SRNO INT NOT NULL AUTO_INCREMENT,
            NAME VARCHAR(50) NOT NULL,
            CLASS VARCHAR(20) NOT NULL,
            SEC VARCHAR(10) NOT NULL,
            ADDRESS VARCHAR(100) NOT NULL,
            PARENTS_NAME VARCHAR(50) NOT NULL,
            MOBILE_NO VARCHAR(20) NOT NULL,
            tc_issued TINYINT(1) DEFAULT 0,
            STATUS VARCHAR(10) DEFAULT 'Active',
            PRIMARY KEY (SRNO)
        )
    """)

    # 3. STUDENT_LIBRARY TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_library (
            ISSUE_ID INT NOT NULL AUTO_INCREMENT,
            STUDENT_SRNO INT NOT NULL,
            BOOK_ID INT NOT NULL,
            ISSUE_DATE DATE NOT NULL,
            DUE_DATE DATE NOT NULL,
            RETURN_DATE DATE DEFAULT NULL,
            FINE DECIMAL(8,2) DEFAULT 0.00,
            FINE_PAID TINYINT(1) DEFAULT 0,
            PRIMARY KEY (ISSUE_ID),
            KEY (STUDENT_SRNO),
            KEY (BOOK_ID),
            CONSTRAINT fk_student_library_student
                FOREIGN KEY (STUDENT_SRNO) REFERENCES student (SRNO),
            CONSTRAINT fk_student_library_book
                FOREIGN KEY (BOOK_ID) REFERENCES book (SRNO)
        )
    """)

    # 4. USERS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            USER_ID INT NOT NULL AUTO_INCREMENT,
            USERNAME VARCHAR(50) NOT NULL,
            PASSWORD_HASH VARCHAR(128) NOT NULL,
            FULL_NAME VARCHAR(50) NOT NULL,
            ROLE VARCHAR(20) DEFAULT 'Admin',
            CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (USER_ID),
            UNIQUE KEY (USERNAME)
        )
    """)

    # Seed default admin user from environment variables if table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        if DEFAULT_ADMIN_PASSWORD:
            default_pwd_hash = hash_password(DEFAULT_ADMIN_PASSWORD)
            cursor.execute(
                """
                INSERT INTO users (USERNAME, PASSWORD_HASH, FULL_NAME, ROLE)
                VALUES (%s, %s, %s, %s)
                """,
                (DEFAULT_ADMIN_USER, default_pwd_hash, DEFAULT_ADMIN_NAME, "Admin")
            )

    # Self-healing upgrades if tables existed from older schemas
    try:
        cursor.execute("ALTER TABLE book ADD COLUMN STATUS VARCHAR(10) DEFAULT 'ACTIVE'")
    except s.Error:
        pass

    try:
        cursor.execute("ALTER TABLE book MODIFY COLUMN SRNO INT NOT NULL AUTO_INCREMENT")
    except s.Error:
        pass

    try:
        cursor.execute("ALTER TABLE book MODIFY COLUMN BOOK_NAME VARCHAR(100) NOT NULL")
    except s.Error:
        pass

    try:
        cursor.execute("ALTER TABLE student MODIFY COLUMN NAME VARCHAR(50) NOT NULL")
        cursor.execute("ALTER TABLE student MODIFY COLUMN ADDRESS VARCHAR(100) NOT NULL")
        cursor.execute("ALTER TABLE student MODIFY COLUMN PARENTS_NAME VARCHAR(50) NOT NULL")
    except s.Error:
        pass

    connection.commit()
    print("All tables checked and verified successfully.")

except s.Error as e:
    if connection and connection.is_connected():
        connection.rollback()
    print("Database setup notice:", e)

finally:
    if cursor is not None:
        cursor.close()
    if connection is not None and connection.is_connected():
        connection.close()
