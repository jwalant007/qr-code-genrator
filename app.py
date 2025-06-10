import os
import mysql.connector
import qrcode
import logging
import warnings
from flask import Flask, render_template, request, send_file
from waitress import serve
from io import BytesIO

# ✅ Suppress warnings globally
warnings.filterwarnings("ignore")

# ✅ Set up logging
logging.basicConfig(level=logging.INFO)

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "152.58.35.76"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "Jwalant_007"),
            database=os.getenv("DB_NAME", "listdb"),
            port=int(os.getenv("DB_PORT", "3306")),
            connect_timeout=10  # Set timeout to prevent hanging connections
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

    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT name, subject, marks, total_marks FROM students WHERE LOWER(name) = LOWER(%s)"
        cursor.execute(query, (name.strip(),))
        result = cursor.fetchone()
        
        logging.info(f"✅ Retrieved student data: {result}")
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
        return render_template("student.html", name=name, student=student_data)

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logging.info(f"🚀 Running Flask app on port {port} with Waitress")
    serve(app, host="0.0.0.0", port=port)