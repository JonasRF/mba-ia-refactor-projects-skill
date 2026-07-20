const TokenService = require('../services/tokenService');
const { AuthError, ForbiddenError } = require('../errors/domainErrors');

function requireAuth(req, _res, next) {
    const header = req.headers.authorization || '';
    const [scheme, token] = header.split(' ');

    if (scheme !== 'Bearer' || !token) {
        return next(new AuthError('Token de autenticação ausente'));
    }

    try {
        req.user = TokenService.verify(token);
        return next();
    } catch {
        return next(new AuthError('Token de autenticação inválido ou expirado'));
    }
}

function requireAdmin(req, res, next) {
    requireAuth(req, res, (err) => {
        if (err) return next(err);
        if (req.user.role !== 'admin') return next(new ForbiddenError('Acesso restrito a administradores'));
        return next();
    });
}

module.exports = { requireAuth, requireAdmin };
