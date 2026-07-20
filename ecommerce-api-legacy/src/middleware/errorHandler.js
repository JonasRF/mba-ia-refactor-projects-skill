const { HTTP_STATUS } = require('../constants/httpStatus');

const STATUS_BY_ERROR_NAME = {
    ValidationError: HTTP_STATUS.BAD_REQUEST,
    NotFoundError: HTTP_STATUS.NOT_FOUND,
    AuthError: HTTP_STATUS.UNAUTHORIZED,
    ForbiddenError: HTTP_STATUS.FORBIDDEN,
    PaymentDeniedError: HTTP_STATUS.BAD_REQUEST,
};

function errorHandler(err, _req, res, _next) {
    const status = STATUS_BY_ERROR_NAME[err.name] || HTTP_STATUS.INTERNAL_SERVER_ERROR;

    if (status === HTTP_STATUS.INTERNAL_SERVER_ERROR) {
        console.error(err);
        return res.status(status).json({ error: 'Erro interno do servidor' });
    }

    return res.status(status).json({ error: err.message });
}

module.exports = errorHandler;
