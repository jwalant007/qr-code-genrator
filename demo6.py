import os
import mysql.connector
import qrcode
from flask import Flask, render_template, request

templates_dir = "templates"
static_dir = "static"
os.makedirs(templates_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)

app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)

DB_CONFIG = {
    "host": "127.0.0.1",  
    "user": "root",  
    "password": "Jwalant_007",  
    "database": "listdb",
    "auth_plugin": "mysql_native_password"
}

import socket
def get_local_ip():
    return socket.gethostbyname(socket.gethostname())

LOCAL_IP = get_local_ip()

def get_student_data(name):
    """Fetch student data from MySQL"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE name = %s", (name,))
        student = cursor.fetchone()
        cursor.close()
        conn.close()

        if student:
            return {desc: val for desc, val in zip(["Name", "sub", "marks", "total_marks", "date"], student)}
        return None
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return None

def generate_qr(name):
    """Generate a QR code linking to the student's details page"""
    student_data = get_student_data(name)
    if student_data:
        qr_url = f"http://{LOCAL_IP}:5000/student/{name}"  

        qr = qrcode.QRCode(version=None, box_size=10, border=5)
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        img_path = os.path.join(static_dir, f"{name}_qrcode.png")
        img.save(img_path)

        return img_path
    return None

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

if __name__ == "_main_":
    app.run(host="0.0.0.0", port=5000, debug=True)