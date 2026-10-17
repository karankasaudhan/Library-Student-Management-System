import mysql.connector as s
from connection import get_connection


def get_books(search_query=None):
    """Fetch all books or filter by search query (name or ID)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if search_query:
            q = f"%{search_query.strip().lower()}%"
            cursor.execute(
                """
                SELECT SRNO, BOOK_NAME, Class, quantity, STATUS
                FROM book
                WHERE LOWER(BOOK_NAME) LIKE %s OR CAST(SRNO AS CHAR) LIKE %s
                ORDER BY SRNO
                """,
                (q, q)
            )
        else:
            cursor.execute(
                "SELECT SRNO, BOOK_NAME, Class, quantity, STATUS FROM book ORDER BY SRNO"
            )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_book_by_id(book_id: int):
    """Fetch single book by its SRNO."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT SRNO, BOOK_NAME, Class, quantity, STATUS FROM book WHERE SRNO = %s",
            (book_id,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def add_book(book_name: str, class_name: str, quantity: int):
    """Add a new book or update quantity if already existing."""
    book_name = book_name.strip().title()
    class_name = class_name.strip()

    if not book_name or not class_name:
        return False, "Book name and class cannot be empty.", None

    if quantity < 0:
        return False, "Quantity cannot be negative.", None

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check if already exists
        cursor.execute("SELECT SRNO FROM book WHERE BOOK_NAME = %s", (book_name,))
        existing = cursor.fetchone()
        if existing:
            return False, f"A book with the name '{book_name}' already exists (ID: {existing[0]}).", None

        status = "ACTIVE" if quantity > 0 else "INACTIVE"
        cursor.execute(
            """
            INSERT INTO book (BOOK_NAME, Class, quantity, STATUS)
            VALUES (%s, %s, %s, %s)
            """,
            (book_name, class_name, quantity, status)
        )
        conn.commit()
        new_id = cursor.lastrowid
        return True, f"Book '{book_name}' added successfully (ID: {new_id}).", new_id
    except s.Error as e:
        conn.rollback()
        return False, f"Database error: {e}", None
    finally:
        cursor.close()
        conn.close()


def update_book(book_id: int, book_name: str, class_name: str, quantity: int):
    """Update details for an existing book."""
    book_name = book_name.strip().title()
    class_name = class_name.strip()

    if not book_name or not class_name:
        return False, "Book name and class cannot be empty."

    if quantity < 0:
        return False, "Quantity cannot be negative."

    status = "ACTIVE" if quantity > 0 else "INACTIVE"
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check duplicate name on another ID
        cursor.execute("SELECT SRNO FROM book WHERE BOOK_NAME = %s AND SRNO != %s", (book_name, book_id))
        if cursor.fetchone():
            return False, f"Another book with the name '{book_name}' already exists."

        cursor.execute(
            """
            UPDATE book
            SET BOOK_NAME = %s,
                Class = %s,
                quantity = %s,
                STATUS = %s
            WHERE SRNO = %s
            """,
            (book_name, class_name, quantity, status, book_id)
        )
        conn.commit()
        return True, "Book details updated successfully."
    except s.Error as e:
        conn.rollback()
        return False, f"Database error: {e}"
    finally:
        cursor.close()
        conn.close()


def deactivate_book(book_id: int):
    """Deactivate a book and set quantity to 0."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE book SET quantity = 0, STATUS = 'INACTIVE' WHERE SRNO = %s",
            (book_id,)
        )
        conn.commit()
        return True, "Book deactivated successfully."
    except s.Error as e:
        conn.rollback()
        return False, f"Database error: {e}"
    finally:
        cursor.close()
        conn.close()
