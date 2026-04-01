import json
from flask import Flask, render_template, request, jsonify
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
    
@app.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    university = data.get("university", "").strip()
    
    # check empty fields
    if not name or not email or not university:
        return jsonify(
            {"success": False, "message": "every field must be filled."}
        )
        
    conn = sqlite3.connect("notices.db")
    cursor = conn.cursor()
    
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            university TEXT,
            email TEXT,
            telegram_id TEXT UNIQUE
        )
        """
    )
    
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    existing = cursor.fetchone()
    
    if existing:
        conn.close()
        return jsonify(
            {"success": False, "message": "This email is already registered."}
        )
    
    cursor.execute(
        "INSERT INTO users (name, university, email) VALUES (?, ?, ?)", (name, university, email)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify(
    {"success": True, "message": f"Thank You {name}! You will now receive updates from {university} 🎉"}
    )   

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)