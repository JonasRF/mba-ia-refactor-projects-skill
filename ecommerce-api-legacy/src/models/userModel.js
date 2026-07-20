const bcrypt = require('bcrypt');
const { dbGet, dbRun } = require('../database/connection');
const config = require('../config');

const UserModel = {
    async findByEmail(email) {
        return dbGet('SELECT id, name, email, role FROM users WHERE email = ?', [email]);
    },

    async findAuthByEmail(email) {
        return dbGet('SELECT id, name, email, pass, role FROM users WHERE email = ?', [email]);
    },

    async create({ name, email, password, role = 'user' }) {
        const passHash = await bcrypt.hash(password, config.bcryptSaltRounds);
        const result = await dbRun(
            'INSERT INTO users (name, email, pass, role) VALUES (?, ?, ?, ?)',
            [name, email, passHash, role]
        );
        return result.lastID;
    },

    async verifyPassword(plainPassword, passwordHash) {
        return bcrypt.compare(plainPassword, passwordHash);
    },

    async delete(userId) {
        const result = await dbRun('DELETE FROM users WHERE id = ?', [userId]);
        return result.changes;
    },
};

module.exports = UserModel;
