const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcryptjs');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const port = 3000;

// Set view engine to ejs for rendering HTML templates
app.set('view engine', 'ejs');

// Middleware to parse form data
app.use(bodyParser.urlencoded({ extended: false }));

// Initialize the SQLite database
const initDb = () => {
  const db = new sqlite3.Database('users.db');
  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT NOT NULL UNIQUE,
      password TEXT NOT NULL
    )
  `);
  db.close();
};

initDb();

// Routes

// Redirect to login page
app.get('/', (req, res) => {
  res.redirect('/login');
});

// Register route
app.get('/register', (req, res) => {
  res.render('create_account', { error: null });
});

app.post('/register', (req, res) => {
  const { newUsername, newPassword, confirmPassword } = req.body;

  if (newPassword !== confirmPassword) {
    return res.render('create_account', { error: 'Passwords do not match. Please try again.' });
  }

  const hashedPassword = bcrypt.hashSync(newPassword, 10);

  const db = new sqlite3.Database('users.db');
  db.run("INSERT INTO users (username, password) VALUES (?, ?)", [newUsername, hashedPassword], function (err) {
    if (err) {
      if (err.code === 'SQLITE_CONSTRAINT') {
        return res.render('create_account', { error: 'Username already exists. Try a different one.' });
      }
      return res.status(500).send('Database error');
    }
    res.redirect('/login');
  });
  db.close();
});

// Login route
app.get('/login', (req, res) => {
  res.render('login', { error: null });
});

app.post('/login', (req, res) => {
  const { username, password } = req.body;

  const db = new sqlite3.Database('users.db');
  db.get("SELECT password FROM users WHERE username = ?", [username], (err, row) => {
    db.close();
    if (err) {
      return res.status(500).send('Database error');
    }
    if (row && bcrypt.compareSync(password, row.password)) {
      res.redirect('/home');
    } else {
      res.render('login', { error: 'Invalid username or password. Please try again.' });
    }
  });
});

// Home route
app.get('/home', (req, res) => {
  res.render('home');
});

// Set up a static directory for serving HTML, CSS, etc.
app.use(express.static(path.join(__dirname, 'public')));

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
