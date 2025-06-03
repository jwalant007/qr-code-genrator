from flask import Flask, send_file
import mysql.connector
import qrcode
from io import BytesIO

app = Flask(__name__)

# Connect to MySQL
def get_data():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="yourpassword",
        database="yourdb"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT name, score FROM students LIMIT 5")  # Modify the query as needed
    data = cursor.fetchall()
    conn.close()
    return data

@app.route("/generate_qr")
def generate_qr():
    """Generate a QR code with database output"""
    data = get_data()
    formatted_data = "\n".join([f"Name: {row[0]}, Score: {row[1]}" for row in data])

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(formatted_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    qr_io = BytesIO()
    img.save(qr_io, format="PNG")
    qr_io.seek(0)

    return send_file(qr_io, mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True)