import os
import hashlib
from dotenv import load_dotenv
import mysql.connector as s

# Locate and load .env file from the current project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH)

# Environment configuration variables
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "library")

# Default admin configuration from .env for first-time setup
DEFAULT_ADMIN_USER = os.getenv("DEFAULT_ADMIN_USER", "Karan")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "")
DEFAULT_ADMIN_NAME = os.getenv("DEFAULT_ADMIN_NAME", "Administrator")

# Backwards-compatible configuration dictionary
DB_CONFIG = {
    "host": DB_HOST,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_NAME,
    "use_pure": True
}


def get_connection(use_database=True):
    """
    Establish and return a secure MySQL database connection.
    Loads credentials exclusively from environment variables (.env).
    Does NOT leak password on failure.
    """
    conn_params = {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "use_pure": True
    }
    if use_database:
        conn_params["database"] = os.getenv("DB_NAME", "library")

    try:
        connection = s.connect(**conn_params)
        return connection
    except s.Error as err:
        # Provide beginner-friendly guidance without revealing sensitive credentials
        error_code = getattr(err, "errno", None)
        masked_host = conn_params["host"]
        masked_user = conn_params["user"]

        if error_code == 1045:
            user_msg = (
                f"MySQL Authentication Failed for user '{masked_user}' on host '{masked_host}'.\n"
                "Please verify that DB_USER and DB_PASSWORD in your '.env' file are correct."
            )
        elif error_code == 2003:
            user_msg = (
                f"Cannot connect to MySQL server at '{masked_host}'.\n"
                "Please ensure that MySQL service (mysqld / XAMPP / WampServer) is running."
            )
        elif error_code == 1049:
            user_msg = (
                f"Database '{conn_params.get('database')}' does not exist yet.\n"
                "Run initialization or start the application to auto-create the database."
            )
        else:
            user_msg = f"Database connection error (Code {error_code}): {err.msg}"

        # Re-raise standard exception with beginner-friendly message
        raise s.Error(user_msg) from None


def get_cursor(connection, buffered=True):
    """Safely return a cursor with buffered results enabled by default."""
    return connection.cursor(buffered=buffered)


def test_connection():
    """Test database connection health and return status with message."""
    try:
        conn = get_connection(use_database=False)
        if conn.is_connected():
            conn.close()
            return True, "Database server connection successful."
        return False, "Failed to connect to MySQL server."
    except s.Error as e:
        return False, str(e)


def hash_password(password: str) -> str:
    """Hash a password securely using SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against stored SHA-256 hash."""
    return hash_password(plain_password) == hashed_password


def init_db():
    """
    Self-healing initialization:
    Ensures the target database, required tables, columns, and default initial user exist.
    """
    conn = None
    try:
        conn = get_connection(use_database=False)
        cursor = conn.cursor()
        db_name = os.getenv("DB_NAME", "library")

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
        cursor.execute(f"USE `{db_name}`")

        # Table 1: book
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

        # Table 2: student
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

        # Table 3: student_library
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

        # Table 4: users
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

        # Seed initial admin if users table is empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            admin_user = os.getenv("DEFAULT_ADMIN_USER", "Karan")
            admin_pwd = os.getenv("DEFAULT_ADMIN_PASSWORD", "")
            admin_name = os.getenv("DEFAULT_ADMIN_NAME", "Administrator")
            if admin_pwd:
                hashed_admin_pwd = hash_password(admin_pwd)
                cursor.execute(
                    """
                    INSERT INTO users (USERNAME, PASSWORD_HASH, FULL_NAME, ROLE)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (admin_user, hashed_admin_pwd, admin_name, "Admin")
                )

        # Ensure column upgrades for existing schemas
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

        conn.commit()
        cursor.close()
        return True, "Database initialized successfully."
    except s.Error as e:
        return False, str(e)
    finally:
        if conn and conn.is_connected():
            conn.close()
