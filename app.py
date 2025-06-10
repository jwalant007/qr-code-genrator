import os
import mysql.connector
import qrcode
import logging
import warnings
from flask import Flask, render_template, request, send_file, redirect, url_for
from waitress import serve
from io import BytesIO

# ✅ Suppress warnings globally
warnings.filterwarnings("ignore")

# ✅ Set up logging
logging.basicConfig(level=logging.INFO)

# ✅ Create Flask app with static file serving enabled
app = Flask(__name__, static_url_path='/static', template_folder="templates")

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "192.168.206.76"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "Jwalant_007"),
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

@app.route("/")
def index():
    try:
        # ✅ Test database connection before rendering the template
        conn = get_db_connection()
        if not conn:
            return "<h1>❌ Database connection failed</h1>", 500
        conn.close()  # ✅ Close connection after check
        return render_template("index.html")
    except Exception as e:
        logging.error(f"❌ Exception occurred: {str(e)}")
        return f"<h1>❌ Internal Server Error</h1><p>{str(e)}</p>", 500

@app.route("/health")
def health_check():
    return "<h1>🚀 Flask app is running!</h1>"

def insert_student_data(name, subject, marks, total_marks):
    conn = get_db_connection()
    if not conn:
        logging.error("❌ No database connection available")
        return False

    try:
        cursor = conn.cursor()
        query = "INSERT INTO students (name, subject, marks, total_marks) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, subject, marks, total_marks))
        conn.commit()
        cursor.close()
        conn.close()  # ✅ Ensuring the connection is properly closed
        logging.info(f"✅ Successfully inserted student data: {name}")
        return True
    except mysql.connector.Error as err:
        logging.error(f"❌ Error inserting student data: {err}")
        return False

@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form["name"]
        subject = request.form["subject"]
        marks = request.form["marks"]
        total_marks = request.form["total_marks"]

        success = insert_student_data(name, subject, marks, total_marks)
        if success:
            return redirect(url_for("index"))  # ✅ Redirect to home after successful insert

    return render_template("add_student.html", success=None)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logging.info(f"🚀 Running Flask app on port {port} with Waitress")
    app.run(debug=True)  # ✅ Enabled Debug Mode for error visibility
    serve(app, host="192.168.206.76", port=port)