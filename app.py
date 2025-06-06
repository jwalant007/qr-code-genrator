import os
import mysql.connector
import qrcode
import logging
from flask import Flask, render_template, request, send_file, jsonify
from waitress import serve
from io import BytesIO

# Logging setup
logging.basicConfig(level=logging.INFO)

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
        logging.info("✅ Database connected successfully!")
        conn.close()
    except mysql.connector.Error as err:
        logging.error(f"❌ Connection error: {err}")
        exit(1)  # Stop execution if DB connection fails

def fetch_student_data(name):
    """Fetch a specific student's data by name and print the result."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        query = f"SELECT * FROM {TABLE_NAME} WHERE name = %s"
        cursor.execute(query, (name,))
        result = cursor.fetchone()

        conn.close()

        # ✅ Print student data for debugging
        if result:
            logging.info(f"Student Data Found: {result}")
        else:
            logging.warning(f"No data found for student: {name}")

        return result if result else {}

    except mysql.connector.Error as err:
        logging.error(f"❌ Error fetching student data: {err}")
        return {}

def create_app():
    """Initialize Flask app"""
    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    def index():
        qr_path = ""
        if request.method == "POST":
            name = request.form["name"]
            qr_path = f"/generate_qr/{name}"
        return render_template("index.html", qr_path=qr_path)

    @app.route("/generate_qr/<name>")
    def generate_qr(name):
        """Generate a QR code dynamically"""
        qr_url = f"https://qr-code-generator-xpcv.onrender.com/student/{name}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        qr_io = BytesIO()
        img.save(qr_io, format="PNG")
        qr_io.seek(0)

        return send_file(qr_io, mimetype="image/png")

    @app.route("/student/<name>")
    def display_student(name):
        """Fetch and return a specific student's data"""
        student = fetch_student_data(name)
        if request.headers.get("Accept") == "application/json":  # Check if JSON is requested
            return jsonify(student if student else {"error": "Student not found"})
        return render_template("student.html", name=name, student=student)

    return app

app = create_app()

if __name__ == "__main__":
    test_db_connection()  # Ensure DB is reachable before running the app
    port = int(os.getenv("PORT", 5000))
    
    logging.info(f"🚀 Running Flask app on port {port} with Waitress")
    serve(app, host="0.0.0.0", port=port)