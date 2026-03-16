import json
from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__, template_folder="template")

@app.route("/")
def home():
    conn = sqlite3.connect('notices.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    selected_uni = request.args.get('university')
    cursor.execute("SELECT DISTINCT university FROM notices WHERE university IS NOT NULL")
    universities = [row['university'] for row in cursor.fetchall()]
    
    if selected_uni:
        cursor.execute("SELECT title, link FROM notices WHERE university =?", (selected_uni,))
    else:
        cursor.execute("SELECT title, link FROM notices")

    rows = cursor.fetchall()
    notices_data = [dict(row) for row in rows]
    conn.close()
    
    return render_template(
        "index.html",
        notices_json=json.dumps(notices_data, ensure_ascii=False),
        universities=universities,
        selected_uni=selected_uni
    )

if __name__ == "__main__":
    app.run(debug=True)