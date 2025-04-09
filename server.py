from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DATABASE = "users.db"

# Инициализация БД
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok"})

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"status": "error", "message": "Пустое имя или пароль"})

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            user_id = cursor.lastrowid
            conn.commit()
            return jsonify({"status": "success", "message": "Пользователь зарегистрирован", "user_id": user_id})
        except sqlite3.IntegrityError:
            return jsonify({"status": "error", "message": "Имя пользователя уже занято"})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"status": "error", "message": "Пустое имя или пароль"})

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        if user:
            return jsonify({"status": "success", "user_id": user[0]})
        else:
            return jsonify({"status": "error", "message": "Неверный логин или пароль"})

@app.route("/get_profile", methods=["GET"])
def get_profile():
    user_id = request.args.get("user_id")
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE id=?", (user_id,))
        row = cursor.fetchone()
        if row:
            return jsonify({
                "status": "success",
                "username": row[0],
                "avatar": "ava.jpg"
            })
        return jsonify({"status": "error", "message": "Пользователь не найден"})

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))  # получаем порт из переменных окружения
    app.run(host="0.0.0.0", port=port)  # слушаем на всех интерфейсах
