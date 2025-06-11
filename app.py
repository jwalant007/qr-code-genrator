import os
import mysql.connector
import qrcode
import logging
import warnings
from flask import Flask, render_template, request, send_file, redirect, url_for
from waitress import serve
from io import BytesIO

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="192.168.206.76",
            user="root",
            password="",
            database="listdb",
            port=3306,
            pool_name="mypool",
            pool_size=5
        )
        logging.info("Database connection successful")
        return conn
    except mysql.connector.Error as err:
        logging.error(f"Database connection error: {err}")
        return None

def insert_student_data(name, subject, marks, total_marks):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        query = "INSERT INTO students (name, subject, marks, total_marks) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, subject, marks, total_marks))
        conn.commit()
        logging.info(f"Successfully inserted student: {name}")
        return True
    except mysql.connector.Error as err:
        logging.error(f"Error inserting student data: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def fetch_student_data(name):
    conn = get_db_connection()
    if not conn:
        return {"name": name, "subject": "N/A", "marks": "N/A", "total_marks": "N/A"}
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT name, subject, marks, total_marks FROM students WHERE LOWER(name) = LOWER(%s)"
        cursor.execute(query, (name.strip(),))
        result = cursor.fetchone()
        return result or {"name": name, "subject": "N/A", "marks": "Not Available", "total_marks": "Not Available"}
    except mysql.connector.Error as err:
        logging.error(f"Error fetching student data: {err}")
        return {"name": name, "subject": "N/A", "marks": "Error", "total_marks": "Error"}
    finally:
        conn.close()

def generate_qr_code(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    qr_io = BytesIO()
    img.save(qr_io, format="PNG")
    qr_io.seek(0)
    return qr_io

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        return redirect(url_for("display_student", name=name))
    return render_template("index.html")

@app.route("/generate_qr", methods=["POST"])
def generate_qr_from_form():
    name = request.form["name"]
    qr_url = f"https://qr-code-genrator-xpcv.onrender.com/student/{name}"
    qr_io = generate_qr_code(qr_url)
    return send_file(qr_io, mimetype="image/png")

@app.route("/student/<name>")
def display_student(name):
    student_data = fetch_student_data(name)
    return render_template("student.html", name=name, student=student_data)

@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form["name"]
        subject = request.form["subject"]
        marks = request.form["marks"]
        total_marks = request.form["total_marks"]
        success = insert_student_data(name, subject, marks, total_marks)
        if success:
            return redirect(url_for("display_student", name=name))
    return render_template("add-student.html")
    
if __name__ == "__main__":
    port = 5000
    logging.info(f"Running Flask app on port {port} with Waitress")
    serve(app, host="192.168.206.76", port=port)
    logging.info("Flask app is running successfully")