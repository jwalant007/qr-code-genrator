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
        return render_template("C:\python vs\New folder\templates\index.html", qr_path=qr_path)


    @app.route("/students")
    def get_students():
        """Fetch and display student data from the database"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM students")
            students = cursor.fetchall()
            conn.close()

            return render_template("C:\python vs\New folder\templates\student.html", students=students)  # Render data in HTML template

        except mysql.connector.Error as err:
            return {"error": str(err)}  # Return JSON error response

    return app

# Initialize Flask application for Gunicorn
app = create_app()  # Define the app globally

if __name__ == "__main__":
    test_db_connection()
    port = int(os.getenv("PORT", 5000))

    print(f" Running Flask app on port {port} with Waitress")
    serve(app, host="0.0.0.0", port=port)