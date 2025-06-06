from flask import Flask, render_template_string, request
from flask_sqlalchemy import SQLAlchemy
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)
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

@app.route("/", methods=["GET"])
def index():
    query = request.args.get("search", "")

    if query:
        rows = Record.query.filter(
            (Record.col_a.contains(query)) |
            (Record.col_b.contains(query)) |
            (Record.col_c.contains(query)) |
            (Record.col_d.contains(query)) |
            (Record.col_e.contains(query))
        ).all()
    else:
        rows = Record.query.limit(100).all()

    combined_lines = [
        " | ".join([
            r.col_a or '', r.col_b or '', r.col_c or '', r.col_d or '', r.col_e or ''
        ])
        for r in rows
    ]
    combined_text = "\n".join(combined_lines)

    if not combined_text.strip():
        return "No matching data found."

    # Generate smaller QR code with embedded text
    qr = qrcode.QRCode(box_size=5, border=2)
    qr.add_data(combined_text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    # HTML with QR only
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>QR Code Search</title>
        <style>
            body { font-family: Arial; text-align: center; margin: 20px; }
            input[type="text"] { padding: 8px; width: 300px; }
            button { padding: 8px 12px; }
            img { margin-top: 20px; width: 200px; height: 200px; }
        </style>
    </head>
    <body>
        <h1>Search & Generate QR Code</h1>
        <form method="GET">
            <input type="text" name="search" placeholder="Search..." value="{{ search }}">
            <button type="submit">Search</button>
        </form>

        <img src="data:image/png;base64,{{ qr_data }}" alt="QR Code">
        <p>Scan the QR code to view the data.</p>
    </body>
    </html>
    """

    return render_template_string(html_template, qr_data=qr_base64, search=query)

if __name__ == "_main_":
    app.run(debug=True)