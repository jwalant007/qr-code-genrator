import os
import mysql.connector
import qrcode
from flask import Flask, render_template, request, send_file
from waitress import serve
from io import BytesIO

templates_dir = "templates"
static_dir = "static"
os.makedirs(templates_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "Jwalant_007",
    "database": "listdb"
}

def test_db_connection():
    """Test MySQL connection independently"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("Database connected successfully!")
        conn.close()
    except mysql.connector.Error as err:
        print(f"Connection error: {err}")

def get_student_data(name):
    """Fetch student data from MySQL"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE name = %s", (name,))
        student = cursor.fetchone()
        cursor.close()
        conn.close()

        print(f"Fetched student data: {student}")

        if student:
            return {desc: val for desc, val in zip(["Name", "sub", "marks", "total_marks", "date"], student)}
        return None
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return None

def create_app():
    """Initialize Flask app"""
    app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)

    @app.route("/", methods=["GET", "POST"])
    def index():
        qr_path = None
        if request.method == "POST":
            name = request.form["name"]
            qr_path = generate_qr(name)
        return render_template("index.html", qr_path=qr_path)

    @app.route("/student/<name>")
    def student_page(name):
        student_data = get_student_data(name)
        if student_data:
            return render_template("student.html", student=student_data)
        return "<h1>Student not found</h1>", 404

    @app.route("/generate_qr/<name>")
    def generate_qr(name):
        """Generate a QR code dynamically and return it as an image"""
        student_data = get_student_data(name)
        if student_data:
            qr_url = f"https://qr-code-genrator-xpcv.onrender.com/student/{name}"
            print(f"Generating QR Code for: {name} with URL: {qr_url}")

            qr = qrcode.QRCode(version=None, box_size=10, border=5)
            qr.add_data(qr_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            qr_io = BytesIO()
            img.save(qr_io, format="PNG")
            qr_io.seek(0)

            print(f"QR Code successfully generated for: {name}")

            return send_file(qr_io, mimetype="image/png")

        print("QR Code generation failed!")
        return "<h1>QR Code generation failed!</h1>", 404

    return app

if __name__ == "__main__":
    test_db_connection()  # Test DB connectivity on startup
    app = create_app()
    port = int(os.environ.get("PORT", 5000))

    if os.name == "nt":
        print("Running Flask app with Waitress (Windows)")
        serve(app, host="0.0.0.0", port=port)
    else:
        os.system(f"gunicorn -b 0.0.0.0:{port} app:create_app")
        