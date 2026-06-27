require('dotenv').config();
const express = require('express');
const config  = require('./config');
const { initializeDatabase } = require('./database/connection');
const healthRoutes   = require('./routes/healthRoutes');
const checkoutRoutes = require('./routes/checkoutRoutes');
const reportRoutes   = require('./routes/reportRoutes');
const userRoutes     = require('./routes/userRoutes');

const app = express();
app.use(express.json());

app.use('/', healthRoutes);
app.use('/api', checkoutRoutes);
app.use('/api', reportRoutes);
app.use('/api', userRoutes);

async function start() {
    await initializeDatabase();
    app.listen(config.port, () => {
        console.log(`API rodando na porta ${config.port}`);
    });
}

start();
