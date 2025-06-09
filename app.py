import os
import mysql.connector
import qrcode
import logging
import warnings
from flask import Flask, render_template, request, send_file
from waitress import serve
from io import BytesIO

warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO)

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "152.58.35.76"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "listdb"),
            pool_name="mypool",
            pool_size=5
        )
        if conn.is_connected():
            logging.info("Database connection successful")
        return conn
    except mysql.connector.Error as err:
        logging.error(f"Database connection error: {err}")
        return None

def fetch_student_data(name):
    conn = get_db_connection()
    if not conn:
        logging.error("No database connection available")
        return {
            "name": name,
            "subject": "Database Error",
            "marks": "N/A",
            "total_marks": "N/A"
        }

    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT name, subject, marks, total_marks FROM students WHERE LOWER(name) = LOWER(%s)"
        cursor.execute(query, (name.strip(),))
        result = cursor.fetchone()
        conn.close()
        cursor.close()

        logging.info(f"Retrieved student data: {result}")
        return result if result else {
            "name": name,
            "subject": "Not Found",
            "marks": "Not Available",
            "total_marks": "Not Available"
        }
    except mysql.connector.Error as err:
        logging.error(f"Error fetching student data: {err}")
        return {
            "name": name,
            "subject": "Database Error",
            "marks": "N/A",
            "total_marks": "N/A"
        }