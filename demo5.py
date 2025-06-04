import os
import psycopg2
import qrcode
from flask import Flask, render_template, request, send_file
from waitress import serve
from io import BytesIO

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS")
}

def test_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM students")
        count = cursor.fetchone()[0]
        conn.close()
        print(f" PostgreSQL connected! Students in DB: {count}")
    except Exception as err:
        print(f" Connection error: {err}")

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
        qr_url = f"https://qr-code-genrator-xpcv.onrender.com/students/{name}"
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
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, marks, total_marks FROM students WHERE name = %s", (name,))
            row = cursor.fetchone()
            conn.close()

            student = {
                "id": row[0],
                "name": row[1],
                "marks": row[2],
                "total_marks": row[3]
            } if row else None

            return render_template("index.html", student=student)
        except Exception as err:
            return f" Database error: {err}"

    return app

app = create_app()

if __name__ == "__main__":
    test_db_connection()
    port = int(os.getenv("PORT", 5000))
    print(f" Running Flask app on port {port} with Waitress")
    serve(app, host="0.0.0.0", port=port)