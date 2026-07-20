const { dbRun } = require('./connection');

async function createSchema() {
    await dbRun(`CREATE TABLE users (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        name  TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        pass  TEXT NOT NULL,
        role  TEXT NOT NULL DEFAULT 'user'
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
}

module.exports = { createSchema };
