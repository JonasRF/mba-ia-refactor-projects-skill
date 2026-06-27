const crypto = require('crypto');
const { dbGet, dbRun } = require('../database/connection');

const UserModel = {
    async findByEmail(email) {
        return dbGet('SELECT id, name, email FROM users WHERE email = ?', [email]);
    },

    async create({ name, email, password }) {
        const passHash = crypto.createHash('sha256').update(password).digest('hex');
        const result = await dbRun(
            'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
            [name, email, passHash]
        );
        return result.lastID;
    },

    async delete(userId) {
        const result = await dbRun('DELETE FROM users WHERE id = ?', [userId]);
        return result.changes;
    },
};

module.exports = UserModel;
