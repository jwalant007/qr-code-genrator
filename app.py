import os
import mysql.connector
import qrcode
import logging
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
from waitress import serve
from io import BytesIO

load_dotenv()
logging.basicConfig(level=logging.INFO)

def get_db_connection():
    try:
        db_host = os.getenv("DB_HOST", "localhost")
        db_user = os.getenv("DB_USER", "root")
        db_password = os.getenv("DB_PASSWORD", "")
        db_name = os.getenv("DB_NAME", "listdb")

        logging.info(f"Connecting to MySQL: host={db_host}, db={db_name}")

        if not all([db_host, db_user, db_name]):
            logging.warning("Missing required environment variables.")
            return None

        conn = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )

        if conn.is_connected():
            logging.info("Database connection successful")
        return conn
    except mysql.connector.Error as err:
        logging.error(f"Database connection error: {err}")
        return None

'''def setup_database():
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                subject VARCHAR(100),
                marks INT,
                total_marks INT
            )
        """)
        conn.commit()
        logging.info("Students table verified/created successfully")
        cursor.close()
        conn.close()    
    except mysql.connector.Error as err:
        logging.error(f"Database setup error: {err}")'''

def fetch_student_data(name):
    conn = get_db_connection()
    if not conn:
        logging.error("No database connection available")
        return False
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, subject, marks, total_marks FROM students WHERE LOWER(name) = LOWER(%s)", (name.strip(),))
        result = cursor.fetchone()


        logging.info(f"Retrieved student data: {result}")

        return result if result else {
            "name": name,
            "subject": "Not Found",
            "marks": "Not Available",
            "total_marks": "Not Available"
        }
    
    except mysql.connector.Error as err:
        logging.error(f"Error fetching student data: {err}")
        return {
            "name": name,
            "subject": "Database Error",
            "marks": "N/A",
            "total_marks": "N/A"
        }

   

def insert_student_data(name, subject, marks, total_marks):
    conn = get_db_connection()
    if not conn:
        logging.error("No database connection available")
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name, subject, marks, total_marks) VALUES (%s, %s, %s, %s)", 
                       (name, subject, marks, total_marks))
        conn.commit()
        cursor.close()
        conn.close()
        logging.info(f"Student '{name}' added successfully")
        return True
    except mysql.connector.Error as err:
        logging.error(f"Error inserting student data: {err}")
        return False

def create_app():
    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    def index():
        qr_path = ""
        if request.method == "POST":
            name = request.form["name"]
            subject = request.form.get("subject")
            marks = request.form.get("marks")
            total_marks = request.form.get("total_marks")
            qr_path = f"/generate_qr/{name}"
            if not all([name, subject, marks, total_marks]):
                return "All fields are required", 400

            if insert_student_data(name, subject, marks, total_marks):
                return render_template("index.html", qr_path=qr_path)
            else:
                return "Failed to add student", 500
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
        return render_template("student.html", student=student_data)

    return app

'''setup_database()'''
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.debug = True
    logging.info(f"Running Flask app on port {port} with Waitress")
    serve(app, host="127.0.0.1", port=port)