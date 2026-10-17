import mysql.connector as s
from connection import get_connection


def get_summary():
    """Fetch all high-level KPI metrics for the library."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Total titles & available copies
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(quantity), 0) FROM book")
        titles, available = cursor.fetchone()
        titles = titles or 0
        available = available or 0

        # Currently issued
        cursor.execute("SELECT COUNT(*) FROM student_library WHERE RETURN_DATE IS NULL")
        issued = cursor.fetchone()[0] or 0

        # Total copies = in-stock + out-on-loan
        total_copies = available + issued

        # Total & active students
        cursor.execute("""
            SELECT COUNT(*),
                   SUM(CASE WHEN UPPER(STATUS) = 'ACTIVE' THEN 1 ELSE 0 END)
            FROM student
        """)
        total_students, active_students = cursor.fetchone()
        total_students = total_students or 0
        active_students = active_students or 0

        # Overdue books
        cursor.execute("SELECT COUNT(*) FROM student_library WHERE RETURN_DATE IS NULL AND DUE_DATE < CURDATE()")
        overdue = cursor.fetchone()[0] or 0

        # Total pending fines
        cursor.execute("""
            SELECT COALESCE(SUM(
                CASE
                    WHEN RETURN_DATE IS NULL AND DUE_DATE < CURDATE()
                    THEN DATEDIFF(CURDATE(), DUE_DATE) * 2
                    WHEN RETURN_DATE IS NOT NULL AND (FINE_PAID = 0 OR FINE_PAID IS NULL)
                    THEN COALESCE(FINE, 0)
                    ELSE 0
                END
            ), 0)
            FROM student_library
        """)
        pending_fines = float(cursor.fetchone()[0] or 0.0)

        return {
            "total_titles": titles,
            "available_copies": available,
            "issued_books": issued,
            "total_copies": total_copies,
            "total_students": total_students,
            "active_students": active_students,
            "overdue_books": overdue,
            "pending_fines": pending_fines
        }
    finally:
        cursor.close()
        conn.close()


def get_overdue_report():
    """Fetch detailed overdue books list."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT
                sl.ISSUE_ID,
                st.SRNO,
                st.NAME,
                st.MOBILE_NO,
                b.BOOK_NAME,
                sl.DUE_DATE,
                DATEDIFF(CURDATE(), sl.DUE_DATE) AS LATE_DAYS,
                DATEDIFF(CURDATE(), sl.DUE_DATE) * 2 AS FINE
            FROM student_library AS sl
            JOIN student AS st ON sl.STUDENT_SRNO = st.SRNO
            JOIN book AS b ON sl.BOOK_ID = b.SRNO
            WHERE sl.RETURN_DATE IS NULL AND sl.DUE_DATE < CURDATE()
            ORDER BY sl.DUE_DATE
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_pending_fines_report():
    """Fetch list of all issues with unpaid fines."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT
                sl.ISSUE_ID,
                st.SRNO,
                st.NAME,
                b.BOOK_NAME,
                sl.DUE_DATE,
                CASE
                    WHEN sl.RETURN_DATE IS NULL AND sl.DUE_DATE < CURDATE()
                    THEN DATEDIFF(CURDATE(), sl.DUE_DATE) * 2
                    WHEN sl.RETURN_DATE IS NOT NULL AND (sl.FINE_PAID = 0 OR sl.FINE_PAID IS NULL)
                    THEN COALESCE(sl.FINE, 0)
                    ELSE 0
                END AS PENDING_FINE
            FROM student_library AS sl
            JOIN student AS st ON sl.STUDENT_SRNO = st.SRNO
            JOIN book AS b ON sl.BOOK_ID = b.SRNO
            WHERE
                (sl.RETURN_DATE IS NULL AND sl.DUE_DATE < CURDATE())
                OR
                (sl.RETURN_DATE IS NOT NULL AND (sl.FINE_PAID = 0 OR sl.FINE_PAID IS NULL) AND COALESCE(sl.FINE, 0) > 0)
            ORDER BY sl.DUE_DATE
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_monthly_report():
    """Fetch counts of books issued and returned this current month."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT
                (SELECT COUNT(*) FROM student_library
                 WHERE YEAR(ISSUE_DATE) = YEAR(CURDATE()) AND MONTH(ISSUE_DATE) = MONTH(CURDATE())),
                (SELECT COUNT(*) FROM student_library
                 WHERE RETURN_DATE IS NOT NULL
                   AND YEAR(RETURN_DATE) = YEAR(CURDATE()) AND MONTH(RETURN_DATE) = MONTH(CURDATE()))
        """)
        issued, returned = cursor.fetchone()
        return {
            "issued_this_month": issued or 0,
            "returned_this_month": returned or 0
        }
    finally:
        cursor.close()
        conn.close()
