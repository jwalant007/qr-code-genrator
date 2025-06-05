import os
import mysql.connector
import qrcode
from flask import Flask, render_template, request, send_file, redirect, url_for
from waitress import serve
from io import BytesIO

# ✅ DB Configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "jwalant"),
    "database": os.getenv("DB_NAME", "listdb"),
    "port": int(os.getenv("DB_PORT", 3306))
}

TABLE_NAME = os.getenv("TABLE_NAME", "students")

# ✅ Test DB Connection
def test_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("✅ Database connected successfully!")
        conn.close()
    except mysql.connector.Error as err:
        print(f"❌ Connection error: {err}")

# ✅ Fetch all data (Optional, for listing)
def fetch_data():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        result = cursor.fetchall()
        conn.close()
        return result
    except mysql.connector.Error as err:
        print(f"❌ Error fetching data: {err}")
        return []

# ✅ Fetch specific student
def fetch_student_data(name):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE name = %s", (name,))
        result = cursor.fetchone()
        conn.close()
        return result if result else {}
    except mysql.connector.Error as err:
        print(f"❌ Error fetching student data: {err}")
        return {}

# ✅ Flask App Setup
def create_app():
    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    def index():
        qr_path = ""
        student_data = {}
        if request.method == "POST":
            name = request.form["name"]
            student_data = fetch_student_data(name)

            if student_data:
                return redirect(url_for("generate_qr", name=name))
            else:
                return "<h2>Student not found</h2>", 404

        return render_template("index.html", qr_path=qr_path)

    @app.route("/generate_qr/<name>")
    def generate_qr(name):
        """Generate QR code with embedded student data"""
        student = fetch_student_data(name)
        if not student:
            return "<h2>Student not found</h2>", 404

        # Embed actual data into QR code
        data_string = (
            f"Name: {student['name']}\n"
            f"Subject: {student['sub']}\n"
            f"Marks: {student['marks']}/{student['total_marks']}\n"
            f"Date: {student['date']}"
        )

        qr = qrcode.make(data_string)
        qr_io = BytesIO()
        qr.save(qr_io, format="PNG")
        qr_io.seek(0)

        return send_file(qr_io, mimetype="image/png")

    @app.route("/student/<name>")
    def display_student(name):
        student = fetch_student_data(name)
        if student:
            return render_template("student.html", student=student)
        return "<h2>Student not found</h2>", 404

    return app

# ✅ Run App
app = create_app()

if __name__ == "__main__":
    test_db_connection()
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Running Flask app on http://localhost:{port}")
    serve(app, host="0.0.0.0", port=port)