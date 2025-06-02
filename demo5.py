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
        print(" Database connected successfully!")
        conn.close()
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
        qr_url = f"http://0.0.0.1:5000/student/{name}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        qr_io = BytesIO()
        img.save(qr_io, format="PNG")
        qr_io.seek(0)

        return send_file(qr_io, mimetype="image/png")

    return app

# Initialize Flask application for Gunicorn
app = create_app()  # Define the app globally

if __name__ == "__main__":
    test_db_connection()
    port = int(os.getenv("PORT", 5000))

    print(f" Running Flask app on port {port} with Waitress")
    serve(app, host="0.0.0.0", port=port)
