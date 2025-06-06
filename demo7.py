from flask import Flask, render_template, Response
from flask_sqlalchemy import SQLAlchemy
import qrcode
from io import BytesIO

app = Flask(__name__)

# SQLite DB setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

# Define your table
class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    col_a = db.Column(db.String(100))
    col_b = db.Column(db.String(100))
    col_c = db.Column(db.String(100))
    col_d = db.Column(db.String(100))
    col_e = db.Column(db.String(100))

# Create the table
with app.app_context():
    db.create_all()


@app.route("/add-sample")
def add_sample():
    sample_data = [
        Record(col_a="Alice", col_b="Physics", col_c="A+", col_d="Pass", col_e="2025"),
        Record(col_a="Bob", col_b="Chemistry", col_c="B", col_d="Pass", col_e="2025"),
        Record(col_a="Charlie", col_b="Maths", col_c="A", col_d="Pass", col_e="2025")
    ]
    db.session.add_all(sample_data)
    db.session.commit()
    return "Sample data added!"

# Main QR display route
@app.route("/")
def index():
    # Load from DB
    rows = Record.query.limit(100).all()
    combined_text = "\n".join([
        " | ".join([r.col_a, r.col_b, r.col_c, r.col_d, r.col_e])
        for r in rows
    ])
    # Create QR code
    qr_img = qrcode.make(combined_text)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)
    img_data = buffer.read()

    return Response(img_data, mimetype='image/png')

if __name__ == "_main_":
    app.run(debug=True)
