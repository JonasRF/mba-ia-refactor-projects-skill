const UserModel = require('../models/userModel');
const TokenService = require('../services/tokenService');
const { AuthError } = require('../errors/domainErrors');

const AuthController = {
    async login({ email, password }) {
        const user = await UserModel.findAuthByEmail(email);
        if (!user) throw new AuthError('Credenciais inválidas');

        const passwordMatches = await UserModel.verifyPassword(password, user.pass);
        if (!passwordMatches) throw new AuthError('Credenciais inválidas');

        const token = TokenService.sign({ sub: user.id, role: user.role });

        return {
            token,
            user: { id: user.id, name: user.name, email: user.email, role: user.role },
        };
    },
};

module.exports = AuthController;
