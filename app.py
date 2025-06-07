import os
import mysql.connector
import qrcode
import logging
from flask import Flask, render_template, request, send_file
from waitress import serve
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logging.info(f"Connecting to MySQL: host={os.getenv('DB_HOST')} db={os.getenv('DB_NAME')}")

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "listdb"),
            port=int(os.getenv("DB_PORT", 3306))
        )
        if conn.is_connected():
            logging.info("Database connection successful")
        return conn
    except mysql.connector.Error as err:
        logging.error(f"Database connection error: {err}")
        return None

def fetch_student_data(name):
    conn = get_db_connection()
    if conn is None:
        return {}
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM students WHERE LOWER(name) = LOWER(%s)"
        cursor.execute(query, (name.strip(),))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            logging.info(f"Student data found: {result}")
        else:
            logging.warning("No student found with provided name")
        return result if result else {}
    except mysql.connector.Error as err:
        logging.error(f"Error fetching student data: {err}")
        return {}

def create_app():
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
        qr_url = f"https://qr-code-genrator-xpcv.onrender.com/student/{name}"
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
        student_data = fetch_student_data(name)
        if not student_data:
            return render_template("404.html", name=name), 404
        return render_template("student.html", name=name, student=student_data)

    return app

app = create_app()

if __name__ == "__main__":
    host = os.getenv("Host","localhost"),
    database=os.getenv("DB", "listdb"),
    port = int(os.getenv("PORT", 5000))
    app.debug = True
    conn_test = get_db_connection()
    if conn_test:
        conn_test.close()
    logging.info(f"Running Flask app on port {port} with Waitress")
    serve(app, host="0.0.0.0", port=port)