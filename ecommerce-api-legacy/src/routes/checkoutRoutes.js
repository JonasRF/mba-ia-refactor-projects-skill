const { Router } = require('express');
const CheckoutController = require('../controllers/checkoutController');
const { ValidationError } = require('../errors/domainErrors');
const { HTTP_STATUS } = require('../constants/httpStatus');
const { requireAuth } = require('../middleware/authMiddleware');

const router = Router();

function parseCheckoutBody(body) {
    const { userName, email, password, courseId, cardNumber } = body;

    if (!userName || !email || !courseId || !cardNumber) {
        throw new ValidationError('Campos obrigatórios ausentes: userName, email, courseId, cardNumber');
    }

    const parsedCourseId = parseInt(courseId, 10);
    if (isNaN(parsedCourseId) || parsedCourseId <= 0) {
        throw new ValidationError('courseId deve ser um número inteiro positivo');
    }

    return { userName, email, password: password || '', courseId: parsedCourseId, cardNumber };
}

router.post('/checkout', requireAuth, async (req, res, next) => {
    try {
        const parsed = parseCheckoutBody(req.body || {});
        const result = await CheckoutController.checkout(parsed);
        return res.status(HTTP_STATUS.CREATED).json({ msg: 'Sucesso', enrollment_id: result.enrollmentId });
    } catch (err) {
        return next(err);
    }
});

module.exports = router;
