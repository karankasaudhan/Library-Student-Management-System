from datetime import date, timedelta
import mysql.connector as s
from connection import get_connection


def issue_book(student_srno: int, book_id: int):
    """Issue a book to an active student."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check student
        cursor.execute("SELECT NAME, STATUS FROM student WHERE SRNO = %s", (student_srno,))
        st = cursor.fetchone()
        if not st:
            return False, f"Student with SRNO {student_srno} not found.", None

        student_name, student_status = st
        if str(student_status).upper() != "ACTIVE":
            return False, f"Student '{student_name}' is INACTIVE. Books cannot be issued.", None

        # Check book
        cursor.execute("SELECT BOOK_NAME, quantity, STATUS FROM book WHERE SRNO = %s", (book_id,))
        bk = cursor.fetchone()
        if not bk:
            return False, f"Book with ID {book_id} not found.", None

        book_name, quantity, book_status = bk
        if str(book_status).upper() != "ACTIVE":
            return False, f"Book '{book_name}' is marked as INACTIVE.", None

        if quantity <= 0:
            return False, f"No available copies in stock for '{book_name}'.", None

        # Check duplicate active issue
        cursor.execute(
            """
            SELECT ISSUE_ID FROM student_library
            WHERE STUDENT_SRNO = %s AND BOOK_ID = %s AND RETURN_DATE IS NULL
            """,
            (student_srno, book_id)
        )
        if cursor.fetchone():
            return False, f"Student '{student_name}' already has an active issued copy of '{book_name}'.", None

        issue_date = date.today()
        due_date = issue_date + timedelta(days=7)

        # Decrement quantity & insert issue record
        cursor.execute("UPDATE book SET quantity = quantity - 1 WHERE SRNO = %s AND quantity > 0", (book_id,))
        cursor.execute(
            """
            INSERT INTO student_library (STUDENT_SRNO, BOOK_ID, ISSUE_DATE, DUE_DATE)
            VALUES (%s, %s, %s, %s)
            """,
            (student_srno, book_id, issue_date, due_date)
        )
        issue_id = cursor.lastrowid
        conn.commit()

        details = {
            "issue_id": issue_id,
            "student_name": student_name,
            "book_name": book_name,
            "issue_date": str(issue_date),
            "due_date": str(due_date)
        }
        return True, f"Book '{book_name}' issued successfully to '{student_name}'!", details

    except s.Error as e:
        conn.rollback()
        return False, f"Database error: {e}", None
    finally:
        cursor.close()
        conn.close()


def return_book(issue_id: int):
    """Return an issued book, calculate fine, and restore stock."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT sl.BOOK_ID, sl.ISSUE_DATE, sl.DUE_DATE, b.BOOK_NAME, s.NAME
            FROM student_library sl
            JOIN book b ON sl.BOOK_ID = b.SRNO
            JOIN student s ON sl.STUDENT_SRNO = s.SRNO
            WHERE sl.ISSUE_ID = %s AND sl.RETURN_DATE IS NULL
            """,
            (issue_id,)
        )
        record = cursor.fetchone()
        if not record:
            return False, f"No active issue record found with Issue ID {issue_id}.", None

        book_id, issue_date, due_date, book_name, student_name = record
        return_date = date.today()
        late_days = max(0, (return_date - due_date).days)
        fine = late_days * 2
        fine_paid = 1 if fine == 0 else 0

        cursor.execute(
            """
            UPDATE student_library
            SET RETURN_DATE = %s,
                FINE = %s,
                FINE_PAID = %s
            WHERE ISSUE_ID = %s AND RETURN_DATE IS NULL
            """,
            (return_date, fine, fine_paid, issue_id)
        )

        cursor.execute(
            """
            UPDATE book
            SET quantity = quantity + 1,
                STATUS = 'ACTIVE'
            WHERE SRNO = %s
            """,
            (book_id,)
        )

        conn.commit()

        details = {
            "issue_id": issue_id,
            "student_name": student_name,
            "book_name": book_name,
            "late_days": late_days,
            "fine": fine,
            "fine_paid": bool(fine_paid)
        }
        return True, "Book returned successfully.", details

    except s.Error as e:
        conn.rollback()
        return False, f"Database error: {e}", None
    finally:
        cursor.close()
        conn.close()


def pay_fine(issue_id: int):
    """Mark an unpaid fine as paid."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT FINE, FINE_PAID, RETURN_DATE FROM student_library WHERE ISSUE_ID = %s",
            (issue_id,)
        )
        rec = cursor.fetchone()
        if not rec:
            return False, f"Issue record #{issue_id} not found."

        fine, fine_paid, return_date = rec
        if return_date is None:
            return False, "The book must be returned before processing fine payment."

        fine_val = float(fine or 0.0)
        if fine_val <= 0:
            return False, "No fine is due for this record."

        if fine_paid:
            return False, "Fine for this issue has already been marked as PAID."

        cursor.execute("UPDATE student_library SET FINE_PAID = 1 WHERE ISSUE_ID = %s", (issue_id,))
        conn.commit()
        return True, f"Fine of Rs. {fine_val:.2f} marked as PAID successfully."

    except s.Error as e:
        conn.rollback()
        return False, f"Database error: {e}"
    finally:
        cursor.close()
        conn.close()


def get_active_issues():
    """Fetch all currently issued books."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT l.ISSUE_ID, l.STUDENT_SRNO, s.NAME, l.BOOK_ID, b.BOOK_NAME, l.ISSUE_DATE, l.DUE_DATE
            FROM student_library l
            JOIN student s ON l.STUDENT_SRNO = s.SRNO
            JOIN book b ON l.BOOK_ID = b.SRNO
            WHERE l.RETURN_DATE IS NULL
            ORDER BY l.DUE_DATE
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_student_history(student_srno: int):
    """Fetch complete issue and return history for a student."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT NAME FROM student WHERE SRNO = %s", (student_srno,))
        st = cursor.fetchone()
        if not st:
            return None, "Student not found."

        cursor.execute(
            """
            SELECT l.ISSUE_ID, b.BOOK_NAME, l.ISSUE_DATE, l.DUE_DATE, l.RETURN_DATE, COALESCE(l.FINE, 0), l.FINE_PAID
            FROM student_library l
            JOIN book b ON l.BOOK_ID = b.SRNO
            WHERE l.STUDENT_SRNO = %s
            ORDER BY l.ISSUE_ID DESC
            """,
            (student_srno,)
        )
        return {"student_name": st[0], "records": cursor.fetchall()}, "Success"
    finally:
        cursor.close()
        conn.close()
