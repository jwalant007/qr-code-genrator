import os
import mysql.connector
import qrcode
import logging
import warnings  
import dotenv  
from flask import Flask, render_template, request, send_file, jsonify
from waitress import serve
from gunicorn.app.wsgiapp import run  
from io import BytesIO  

# ✅ Load environment variables securely
dotenv.load_dotenv()

warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO)

def get_db_connection():
    """ Establishes and returns a database connection, ensuring proper closure """
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        if conn.is_connected():
            logging.info("✅ Database connection successful")
        return conn
    except mysql.connector.Error as err:
        logging.error(f"❌ Database connection error: {err}")
        return None

def fetch_student_data(name):
    """✅ Fetch student data with case-insensitive search"""
    conn = get_db_connection()
    if not conn:
        logging.error("❌ No database connection available")
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT name, subject, marks, total_marks FROM students WHERE LOWER(name) = LOWER(%s)"
        cursor.execute(query, (name.strip(),))
        result = cursor.fetchone()
        cursor.close()
        conn.close()  # ✅ Close connection to prevent leaks

        logging.info(f"✅ Retrieved student data: {result}")
        return result if result else {"error": "Student not found"}
    except mysql.connector.Error as err:
        logging.error(f"❌ Error fetching student data: {err}")
        return jsonify({"error": "Database query failed"}), 500

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
        """✅ Improved Student Data Retrieval & Error Handling"""
        student_data = fetch_student_data(name)
        return jsonify(student_data), (404 if "error" in student_data else 200)

    return app

# ✅ Ensure Flask app is initialized correctly
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logging.info(f"🚀 Running Flask app on port {port} with Gunicorn")
    run()