const jwt = require('jsonwebtoken');
const config = require('../config');

const TokenService = {
    sign(payload) {
        return jwt.sign(payload, config.jwtSecret, { expiresIn: config.jwtExpiresIn });
    },

    verify(token) {
        return jwt.verify(token, config.jwtSecret);
    },
};

module.exports = TokenService;
