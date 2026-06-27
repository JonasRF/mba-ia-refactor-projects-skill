module.exports = {
    port: parseInt(process.env.PORT || '3000', 10),
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    smtpUser: process.env.SMTP_USER || '',
};
