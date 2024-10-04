from flask import Flask, request, render_template, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# Function to create the database table if it doesn't exist
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Call the function to initialize the database when the app starts
init_db()

@app.route('/')
def home():
    return render_template('create_account.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['newUsername']
    password = request.form['newPassword']
    
    # Hash the password before storing it
    hashed_password = generate_password_hash(password)

    try:
        # Insert the user into the database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()

        # After successful registration, redirect to the login page
        return redirect(url_for('login'))
    except sqlite3.IntegrityError:
        return 'Username already exists. Try a different one.'

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
