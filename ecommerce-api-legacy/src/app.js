const express = require('express');
const config  = require('./config');
const { createSchema } = require('./database/schema');
const { seedDatabase }  = require('./database/seed');
const healthRoutes   = require('./routes/healthRoutes');
const authRoutes     = require('./routes/authRoutes');
const checkoutRoutes = require('./routes/checkoutRoutes');
const reportRoutes   = require('./routes/reportRoutes');
const userRoutes     = require('./routes/userRoutes');
const errorHandler   = require('./middleware/errorHandler');

const app = express();
app.use(express.json());

app.use('/', healthRoutes);
app.use('/api', authRoutes);
app.use('/api', checkoutRoutes);
app.use('/api', reportRoutes);
app.use('/api', userRoutes);

app.use(errorHandler);

async function start() {
    await createSchema();
    if (config.seedDatabase) {
        await seedDatabase();
    }
    app.listen(config.port, () => {
        console.log(`API rodando na porta ${config.port}`);
    });
}

start();
