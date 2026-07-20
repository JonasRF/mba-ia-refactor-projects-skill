const { dbRun } = require('./connection');
const UserModel = require('../models/userModel');

async function seedDatabase() {
    await UserModel.create({
        name: 'Leonan',
        email: 'leonan@fullcycle.com.br',
        password: '123',
        role: 'admin',
    });
     await UserModel.create({
        name: 'João',
        email: 'joao@fullcycle.com.br',
        password: '125',
        role: 'user',
    });

    await dbRun(`INSERT INTO courses (title, price, active) VALUES (?, ?, ?)`,
        ['Clean Architecture', 997.00, 1]);
    await dbRun(`INSERT INTO courses (title, price, active) VALUES (?, ?, ?)`,
        ['Docker', 497.00, 1]);
    await dbRun(`INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)`, [1, 1]);
    await dbRun(`INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)`,
        [1, 997.00, 'PAID']);
}

module.exports = { seedDatabase };
