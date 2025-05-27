import os
import mysql.connector
import qrcode
from flask import Flask, render_template, request
from waitress import serve  
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
    """Generate a QR code linking to the student's details page on Render"""
    student_data = get_student_data(name)
    if student_data:
        qr_url = f"https://qr-code-genrator-xpcv.onrender.com/student/{name}"

        qr = qrcode.QRCode(version=None, box_size=10, border=5)
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        img_path = os.path.join(static_dir, f"{name}_qrcode.png")

        print(f"Generating QR Code for: {name}")
        print(f"Saving QR Code at: {img_path}")

        img.save(img_path)

        return img_path

    print("QR Code generation failed!")  
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  

    if os.name == "nt":  
        print("Running Flask app with Waitress (Windows)")
        serve(app, host="0.0.0.0", port=port)
    else:  
        from gunicorn.app.wsgiapp import run
        run()
