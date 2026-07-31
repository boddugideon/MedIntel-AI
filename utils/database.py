import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from datetime import date, datetime

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "medintel_ai"),
    "connection_timeout": 15,
}


def get_database_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as error:
        print(f"Database connection error: {error}")
        return None


def _serialise(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def save_patient_report(patient_name, age, gender, phone, report_type,
                        report_date, extracted_text, ai_analysis):
    connection = get_database_connection()
    if connection is None:
        return False

    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO patient_reports
                (patient_name, age, gender, phone, report_type, report_date,
                 extracted_text, ai_analysis)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                patient_name, age, gender, phone, report_type, report_date,
                extracted_text, ai_analysis,
            ),
        )
        connection.commit()
        return True
    except Error as error:
        connection.rollback()
        print(f"Save report error: {error}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_all_patient_reports():
    connection = get_database_connection()
    if connection is None:
        return []

    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, patient_name, age, gender, phone,
                   report_type, report_date, created_at
            FROM patient_reports
            ORDER BY id DESC
            """
        )
        rows = cursor.fetchall()
        return [
            {key: _serialise(value) for key, value in row.items()}
            for row in rows
        ]
    except Error as error:
        print(f"Fetch reports error: {error}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_patient_report_by_id(report_id):
    connection = get_database_connection()
    if connection is None:
        return None

    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM patient_reports WHERE id = %s",
            (int(report_id),),
        )
        row = cursor.fetchone()
        if row:
            return {key: _serialise(value) for key, value in row.items()}
        return None
    except (Error, TypeError, ValueError) as error:
        print(f"Fetch selected report error: {error}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()
# =====================================================
# User Registration
# =====================================================

def create_user(full_name, username, email, password):
    connection = get_database_connection()
    if connection is None:
        return False

    cursor = None
    try:
        cursor = connection.cursor()

        query = """
        INSERT INTO users (
            full_name,
            username,
            email,
            password
        )
        VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (
                full_name,
                username,
                email,
                password,
            ),
        )

        connection.commit()
        return True

    except Exception as error:
        print(f"User creation error: {error}")
        return False

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =====================================================
# Check Existing User
# =====================================================

def user_exists(username, email):

    connection = None
    cursor = None

    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT id
        FROM users
        WHERE username = %s
        OR email = %s
        LIMIT 1
        """

        cursor.execute(query, (username, email))
        user = cursor.fetchone()

        return user is not None

    except Exception as error:
        print(f"User check error: {error}")
        return False

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()
            
# =====================================================
# Reset User Password
# =====================================================

def reset_user_password(username_or_email, new_password):

    connection = None
    cursor = None

    try:
        connection = get_database_connection()

        if connection is None:
            return False

        cursor = connection.cursor()

        query = """
        UPDATE users
        SET password = %s
        WHERE username = %s
        OR email = %s
        """

        cursor.execute(
            query,
            (
                new_password,
                username_or_email,
                username_or_email
            )
        )

        connection.commit()

        # rowcount tells us whether a matching user was found
        return cursor.rowcount > 0

    except Exception as error:
        print(f"Password reset error: {error}")
        return False

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()