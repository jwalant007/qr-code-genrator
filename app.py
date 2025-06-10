import os
import mysql.connector
import qrcode
import logging
import warnings
from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify
from waitress import serve
from io import BytesIO

# ✅ Suppress warnings globally
warnings.filterwarnings("ignore")

# ✅ Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_db_connection():
    """ Establishes a database connection using environment variables. """
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "Jwalant_007" ),  # 🔒 Avoid hardcoded credentials
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

def insert_student_data(name, subject, marks, total_marks):
    """ Inserts student data into the database safely. """
    conn = get_db_connection()
    if not conn:
        logging.error("❌ No database connection available")
        return False

    try:
        with conn.cursor() as cursor:
            query = "INSERT INTO students (name, subject, marks, total_marks) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (name, subject, marks, total_marks))
            conn.commit()
            logging.info(f"✅ Successfully inserted student data: {name}")
        return True
    except mysql.connector.Error as err:
        logging.error(f"❌ Error inserting student data: {err}")
        return False
    finally:
        conn.close()  # ✅ Ensure the connection is closed after execution

def fetch_student_data(name):
    """ Retrieves student data from the database. """
    conn = get_db_connection()
    if not conn:
        logging.error("❌ No database connection available")
        return {"name": name, "subject": "N/A", "marks": "N/A", "total_marks": "N/A"}

    try:
        with conn.cursor(dictionary=True) as cursor:
            query = "SELECT name, subject, marks, total_marks FROM students WHERE LOWER(name) = LOWER(%s)"
            cursor.execute(query, (name.strip(),))
            result = cursor.fetchone()
            logging.info(f"✅ Retrieved student data: {result}")
            return result if result else {"name": name, "subject": "N/A", "marks": "Not Available", "total_marks": "Not Available"}
    except mysql.connector.Error as err:
        logging.error(f"❌ Error fetching student data: {err}")
        return {"name": name, "subject": "N/A", "marks": "Error", "total_marks": "Error"}
    finally:
        conn.close()  # ✅ Ensure the connection is closed after execution

def create_app():
    """ Creates and configures the Flask application. """
    app = Flask(__name__, static_url_path='/static')

    @app.route("/", methods=["GET", "POST"])
    def index():
        qr_path = ""
        if request.method == "POST":
            name = request.form["name"]
            qr_path = f"/generate_qr/{name}"
        return render_template("index.html", qr_path=qr_path)

    @app.route("/generate_qr/<name>")
    def generate_qr(name):
        """ Generates and returns a QR code for student details. """
        try:
            qr_url = f"https://qr-code-genrator-xpcv.onrender.com/student/{name}"
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            qr_io = BytesIO()
            img.save(qr_io, format="PNG")
            qr_io.seek(0)

            return send_file(qr_io, mimetype="image/png")
        except Exception as e:
            logging.error(f"❌ Error generating QR code: {e}")
            return jsonify({"error": "Error generating QR code"}), 500

    @app.route("/student/<name>")
    def display_student(name):
        """ Fetches and displays student details. """
        student_data = fetch_student_data(name)
        return render_template("student.html", name=name, student=student_data)

    @app.route("/add_student", methods=["GET", "POST"])
    def add_student():
        """ Allows adding a new student to the database. """
        success = None
        if request.method == "POST":
            name = request.form["name"]
            subject = request.form["subject"]
            marks = request.form["marks"]
            total_marks = request.form["total_marks"]
            success = insert_student_data(name, subject, marks, total_marks)
            if success:
                return redirect(url_for("index"))  # ✅ Redirect to home if insert succeeds

        return render_template("add-student.html", success=success)

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logging.info(f"🚀 Running Flask app on port {port} with Waitress")
    serve(app, host="0.0.0.0", port=port)
    logging.info("✅ Flask app is running successfully")