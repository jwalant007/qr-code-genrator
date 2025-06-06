import os
import mysql.connector
import qrcode
import logging
from flask import Flask, render_template, request, send_file
from waitress import serve
from io import BytesIO

# ✅ Set up logging
logging.basicConfig(level=logging.INFO)

'''DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "listdb"),
    "port": int(os.getenv("DB_PORT", 3306))
}'''
def get_db_connection():
    DB_CONFIG = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="listdb"
    )
    return DB_CONFIG

def fetch_student_data(name):
    """✅ Fetch a specific student's data with case-insensitive search."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = f"SELECT * FROM students WHERE name = BOB"  # Case-insensitive search
        cursor.execute(query,(name ,))
        result = cursor.fetchone()

        conn.close()
        cursor.close()
        return result if result else {}

    except mysql.connector.Error as err:
        logging.error(f"❌ Error fetching student data: {err}")
        return {}

def create_app():
    """✅ Initialize Flask app"""
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
        """✅ Generate a QR code dynamically"""
        qr_url = f"https://qr-code-genrator-xpcv.onrender.com/student/{name}"  # Fixed QR code URL
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
        student = fetch_student_data(name)
        return render_template("student.html", name=name, student=student) 


    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.debug = True
    logging.info(f"🚀 Running Flask app on port {port} with Waitress")
    serve(app, host="127.0.0.1", port=port)