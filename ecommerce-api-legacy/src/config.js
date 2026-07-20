require('dotenv').config();

if (!process.env.JWT_SECRET) {
    throw new Error('JWT_SECRET não definido. Configure a variável de ambiente antes de iniciar a API.');
}

module.exports = {
    port: parseInt(process.env.PORT || '3000', 10),
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    smtpUser: process.env.SMTP_USER || '',
    jwtSecret: process.env.JWT_SECRET,
    jwtExpiresIn: '8h',
    nodeEnv: process.env.NODE_ENV || 'development',
    seedDatabase: (process.env.NODE_ENV || 'development') !== 'production',
    bcryptSaltRounds: 12,
};
