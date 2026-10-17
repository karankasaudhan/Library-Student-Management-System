import mysql.connector as s
from connection import get_connection


def get_students(search_query=None):
    """Fetch all students or filter by name, SRNO, or mobile number."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if search_query:
            q = f"%{search_query.strip().lower()}%"
            cursor.execute(
                """
                SELECT SRNO, NAME, CLASS, SEC, ADDRESS, PARENTS_NAME, MOBILE_NO, tc_issued, STATUS
                FROM student
                WHERE LOWER(NAME) LIKE %s OR CAST(SRNO AS CHAR) LIKE %s OR MOBILE_NO LIKE %s
                ORDER BY SRNO
                """,
                (q, q, q)
            )
        else:
            cursor.execute(
                """
                SELECT SRNO, NAME, CLASS, SEC, ADDRESS, PARENTS_NAME, MOBILE_NO, tc_issued, STATUS
                FROM student
                ORDER BY SRNO
                """
            )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_student_by_srno(srno: int):
    """Fetch single student by SRNO."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT SRNO, NAME, CLASS, SEC, ADDRESS, PARENTS_NAME, MOBILE_NO, tc_issued, STATUS
            FROM student
            WHERE SRNO = %s
            """,
            (srno,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def add_student(name: str, class_name: str, sec: str, address: str, parents_name: str, mobile_no: str):
    """Add a new student record."""
    name = name.strip().title()
    class_name = class_name.strip()
    sec = sec.strip().upper()
    address = address.strip().title()
    parents_name = parents_name.strip().title()
    mobile_no = mobile_no.strip()

    if not name or not class_name or not address or not parents_name:
        return False, "All student details are required.", None

    if not mobile_no.isdigit():
        return False, "Mobile number must contain digits only.", None

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO student (NAME, CLASS, SEC, ADDRESS, PARENTS_NAME, MOBILE_NO, tc_issued, STATUS)
            VALUES (%s, %s, %s, %s, %s, %s, 0, 'Active')
            """,
            (name, class_name, sec, address, parents_name, mobile_no)
        )
        conn.commit()
        new_srno = cursor.lastrowid
        return True, f"Student '{name}' added successfully (SRNO: {new_srno}).", new_srno
    except s.Error as e:
        conn.rollback()
        return False, f"Database error: {e}", None
    finally:
        cursor.close()
        conn.close()


def update_student(srno: int, name: str, class_name: str, sec: str, address: str, parents_name: str, mobile_no: str):
    """Update details of a specific student without affecting other records."""
    name = name.strip().title()
    class_name = class_name.strip()
    sec = sec.strip().upper()
    address = address.strip().title()
    parents_name = parents_name.strip().title()
    mobile_no = mobile_no.strip()

    if not name or not class_name or not address or not parents_name:
        return False, "All fields are required."

    if not mobile_no.isdigit():
        return False, "Mobile number must contain digits only."

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE student
            SET NAME = %s,
                CLASS = %s,
                SEC = %s,
                ADDRESS = %s,
                PARENTS_NAME = %s,
                MOBILE_NO = %s
            WHERE SRNO = %s
            """,
            (name, class_name, sec, address, parents_name, mobile_no, srno)
        )
        conn.commit()
        return True, f"Student #{srno} record updated successfully."
    except s.Error as e:
        conn.rollback()
        return False, f"Database error: {e}"
    finally:
        cursor.close()
        conn.close()


def update_tc_status(srno: int, tc_issued: int, status: str):
    """Update TC issued flag and Active/Inactive status for a student."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE student SET tc_issued = %s, STATUS = %s WHERE SRNO = %s",
            (tc_issued, status, srno)
        )
        conn.commit()
        return True, f"Student #{srno} status updated to '{status}'."
    except s.Error as e:
        conn.rollback()
        return False, f"Database error: {e}"
    finally:
        cursor.close()
        conn.close()
