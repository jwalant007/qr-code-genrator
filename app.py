import os
import mysql.connector
import qrcode
import logging
import warnings
from flask import Flask, render_template, request, send_file, redirect, url_for
from waitress import serve
from io import BytesIO

# ✅ Suppress warnings globally
warnings.filterwarnings("ignore")

# ✅ Set up logging
logging.basicConfig(level=logging.INFO)

# ✅ Create Flask app with static file serving enabled
app = Flask(__name__, template_folder="templates", static_url_path="/static")

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "192.168.206.76"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "Jwalant_007"),
            database=os.getenv("DB_NAME", "listdb"),
            port=int(os.getenv("DB_PORT", "3306")),
            connect_timeout=10
        )
        
        if conn.is_connected():
            logging.info("✅ Database connection successful")
            return conn
        else:
            logging.error("❌ Connection failed")
            return None
    except mysql.connector.Error as err:
        logging.error(f"❌ Database connection error: {err}")
        return None
    
def fetch_student_data(name):
    conn = get_db_connection()
    if not conn:
        logging.error("❌ No database connection available")
        return {
            "name": name,
            "subject": "N/A",
            "marks": "N/A",
            "total_marks": "N/A"
        }
    else:
        logging.info("Connected to database successfully")

    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT name, subject, marks, total_marks FROM students WHERE LOWER(name) = LOWER(%s)"
        cursor.execute(query, (name.strip(),))
        result = cursor.fetchone()
        
        logging.info(f"✅ Retrieved student data: {result}")
        conn.close()  # ✅ Close connection after fetching data

        return result if result else {
            "name": name,
            "subject": "N/A",
            "marks": "Not Available",
            "total_marks": "Not Available"
        }
    except mysql.connector.Error as err:
        logging.error(f"❌ Error fetching student data: {err}")
        return {
            "name": name,
            "subject": "N/A",
            "marks": "Error",
            "total_marks": "Error"
        }

def insert_student_data(name, subject, marks, total_marks):
    conn = get_db_connection()
    if not conn:
        logging.error("❌ No database connection available")
        return False

    try:
        cursor = conn.cursor()
        query = "INSERT INTO students (name, subject, marks, total_marks) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, subject, marks, total_marks))
        conn.commit()
        cursor.close()
        conn.close()  # ✅ Ensuring the connection is properly closed
        logging.info(f"✅ Successfully inserted student data: {name}")
        return True
    except mysql.connector.Error as err:
        logging.error(f"❌ Error inserting student data: {err}")
        return False

@app.route("/")
def index():
    return render_template("qr_code.html")

@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form["name"]
        subject = request.form["subject"]
        marks = request.form["marks"]
        total_marks = request.form["total_marks"]

        success = insert_student_data(name, subject, marks, total_marks)
        if success:
            return redirect(url_for("index"))  # ✅ Redirect to home after successful insert

    return render_template("add_student.html", success=None)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logging.info(f"🚀 Running Flask app on port {port} with Waitress")
    serve(app, host="192.168.206.76", port=port)