const { Router } = require('express');
const AuthController = require('../controllers/authController');
const { ValidationError } = require('../errors/domainErrors');
const { HTTP_STATUS } = require('../constants/httpStatus');

const router = Router();

function parseLoginBody(body) {
    const { email, password } = body;
    if (!email || !password) {
        throw new ValidationError('Campos obrigatórios ausentes: email, password');
    }
    return { email, password };
}

router.post('/login', async (req, res, next) => {
    try {
        const parsed = parseLoginBody(req.body || {});
        const result = await AuthController.login(parsed);
        return res.status(HTTP_STATUS.OK).json(result);
    } catch (err) {
        return next(err);
    }
});

module.exports = router;
