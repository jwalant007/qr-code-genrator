from flask import Flask, request, render_template
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="listdb"
    )

@app.route('/index', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        name = request.form['name']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE name = %s", (name,))
        data = cursor.fetchall()
        conn.close()
        return render_template('student.html', name=name, data=data)
    return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True)

