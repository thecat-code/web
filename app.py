from flask import Flask, request, render_template, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Initialize the database
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

init_db()

@app.route('/')
def index():
    # Redirect to login page
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['newUsername']
        password = request.form['newPassword']
        confirm_password = request.form['confirmPassword']
        
        if password != confirm_password:
            return "Passwords do not match. Please try again."
        
        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            conn.close()

            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return 'Username already exists. Try a different one.'

    return render_template('create_account.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None  # Initialize error message to None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Connect to the database and check if the username exists
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        result = cursor.fetchone()  # Fetch the stored password for the user
        conn.close()

        # If user exists and password matches, redirect to home
        if result and check_password_hash(result[0], password):
            return redirect(url_for('home'))
        else:
            # Set an error message to be displayed on the login page
            error = 'Invalid username or password. Please try again.'

    # Render the login template with error if login fails
    return render_template('login.html', error=error)

@app.route('/home')
def home():
    # This is the page that users are redirected to after successful login
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
