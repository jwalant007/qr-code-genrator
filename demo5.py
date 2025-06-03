import os
import mysql.connector
import qrcode
from flask import Flask, render_template, request, send_file
from waitress import serve
from io import BytesIO

app = Flask(__name__)

# Database Config
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "jwalant"),
    "database": os.getenv("DB_NAME", "listdb"),
    "port": int(os.getenv("DB_PORT", 3306))
}

def get_data():
    """Fetch data from MySQL"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT name, score FROM students LIMIT 5")
    data = cursor.fetchall()
    conn.close()
    return data

@app.route("/", methods=["GET", "POST"])
def index():
    qr_path = ""
    if request.method == "POST":
        name = request.form["name"]
        qr_path = f"/generate_qr/{name}"
    return render_template("index.html", qr_path=qr_path)

@app.route("/generate_qr/<name>")
def generate_qr(name):
  qr = qrcode.QRCode(version=1, box_size=10, border=5)
  qr.add_data("https://www.example.com")  # Test with a simple URL
  qr.make(fit=True)

img =qrcode.make_image(fill_color="black", back_color="white")
img.show()

if __name__ == "__main__":
    app.run(debug=True)