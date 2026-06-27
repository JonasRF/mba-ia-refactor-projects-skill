const sqlite3 = require('sqlite3').verbose();
const crypto = require('crypto');

const db = new sqlite3.Database(':memory:');

function dbGet(sql, params = []) {
    return new Promise((resolve, reject) => {
        db.get(sql, params, (err, row) => {
            if (err) reject(err);
            else resolve(row || null);
        });
    });
}

function dbAll(sql, params = []) {
    return new Promise((resolve, reject) => {
        db.all(sql, params, (err, rows) => {
            if (err) reject(err);
            else resolve(rows || []);
        });
    });
}

function dbRun(sql, params = []) {
    return new Promise((resolve, reject) => {
        db.run(sql, params, function(err) {
            if (err) reject(err);
            else resolve({ lastID: this.lastID, changes: this.changes });
        });
    });
}

async function initializeDatabase() {
    await dbRun(`CREATE TABLE users (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        name  TEXT NOT NULL,
        email TEXT NOT NULL,
        pass  TEXT NOT NULL
    )`);
    await dbRun(`CREATE TABLE courses (
        id     INTEGER PRIMARY KEY AUTOINCREMENT,
        title  TEXT NOT NULL,
        price  REAL NOT NULL,
        active INTEGER NOT NULL DEFAULT 1
    )`);
    await dbRun(`CREATE TABLE enrollments (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id   INTEGER NOT NULL,
        course_id INTEGER NOT NULL
    )`);
    await dbRun(`CREATE TABLE payments (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        enrollment_id INTEGER NOT NULL,
        amount        REAL NOT NULL,
        status        TEXT NOT NULL
    )`);
    await dbRun(`CREATE TABLE audit_logs (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        action     TEXT NOT NULL,
        created_at DATETIME NOT NULL
    )`);

    const seedPassHash = crypto.createHash('sha256').update('123').digest('hex');
    await dbRun(`INSERT INTO users (name, email, pass) VALUES (?, ?, ?)`,
        ['Leonan', 'leonan@fullcycle.com.br', seedPassHash]);
    await dbRun(`INSERT INTO courses (title, price, active) VALUES (?, ?, ?)`,
        ['Clean Architecture', 997.00, 1]);
    await dbRun(`INSERT INTO courses (title, price, active) VALUES (?, ?, ?)`,
        ['Docker', 497.00, 1]);
    await dbRun(`INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)`, [1, 1]);
    await dbRun(`INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)`,
        [1, 997.00, 'PAID']);
}

module.exports = { db, dbGet, dbAll, dbRun, initializeDatabase };
