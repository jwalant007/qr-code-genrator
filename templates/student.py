import os
import mysql.connector
import qrcode
from flask import Flask, render_template, request, send_file
from waitress import serve
from io import BytesIO


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "jwalant"),
    "database": os.getenv("DB_NAME", "listdb"),
    "port": int(os.getenv("DB_PORT", 3306))
}

TABLE_NAME = os.getenv("TABLE_NAME", "students")

def test_db_connection():
    """Test MySQL connection independently"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print(" Database connected successfully!")
        conn.close()
    except mysql.connector.Error as err:
        print(f" Connection error: {err}")

def fetch_student_data(name):
    """Fetch a specific student's data by name."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        query = f"SELECT * FROM {TABLE_NAME} WHERE name = %s"
        cursor.execute(query, (name,))
        result = cursor.fetchone()

        conn.close()
        return result if result else {}  # Returning an empty dict if no student found
    except mysql.connector.Error as err:
        print(f"Error fetching student data: {err}")
        return {}

def create_app():
    """Initialize Flask app"""
    app = Flask(__name__)

     
    def fetch_student_data(name):
            """Fetch a specific student's data by name."""
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor(dictionary=True)

                query = f"SELECT * FROM {TABLE_NAME} WHERE name = {name}"
                cursor.execute(query, (name,))
                result = cursor.fetchone()
                
                print("DEBUG - name:",name)
                print("DEBUG - DB result:",result)                
                conn.close()
                return result if result else {}  # Returning an empty dict if no student found
            except mysql.connector.Error as err:
                print(f"Error fetching student data: {err}")
                return {}

    return app

app = create_app()



