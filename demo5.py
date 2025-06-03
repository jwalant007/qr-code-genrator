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

def test_db_connection():
    """Test MySQL connection independently"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM students")
        count = cursor.fetchone()[0]
        conn.close()
        print(f" Database connected successfully! Students in DB: {count}")
    except mysql.connector.Error as err:
        print(f" Connection error: {err}")

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
        qr_url = f"http://127.0.0.1:5000/students/{name}"  # Local version
        print(f"Generating QR for: {qr_url}")  

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        qr_io = BytesIO()
        img.save(qr_io, format="PNG")
        qr_io.seek(0)

        return send_file(qr_io, mimetype="image/png")

    @app.route("/students/<name>")
    def show_student(name):
        """Fetch student data from MySQL and render template"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, name, marks, total_marks FROM students WHERE name = %s", (name,))
            student = cursor.fetchone()
            conn.close()

            return render_template("student.html", student=student)
        except mysql.connector.Error as err:
            return f" Database connection error: {err}"

    return app

app = create_app()

if __name__ == "__main__":
    test_db_connection()
    port = int(os.getenv("PORT", 5000))
    print(f" Running Flask app on port {port} with Waitress")
    serve(app, host="127.0.0.1", port=port)