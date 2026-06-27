const { Router } = require('express');
const CheckoutController = require('../controllers/checkoutController');

const router = Router();

function parseCheckoutBody(body) {
    const { usr: userName, eml: email, pwd: password, c_id: courseId, card: cardNumber } = body;

    if (!userName || !email || !courseId || !cardNumber) {
        const err = new Error('Campos obrigatórios ausentes: usr, eml, c_id, card');
        err.status = 400;
        throw err;
    }

    const parsedCourseId = parseInt(courseId, 10);
    if (isNaN(parsedCourseId) || parsedCourseId <= 0) {
        const err = new Error('c_id deve ser um número inteiro positivo');
        err.status = 400;
        throw err;
    }

    return { userName, email, password: password || '', courseId: parsedCourseId, cardNumber };
}

router.post('/checkout', async (req, res) => {
    let parsed;
    try {
        parsed = parseCheckoutBody(req.body || {});
    } catch (err) {
        return res.status(err.status || 400).json({ error: err.message });
    }

    try {
        const result = await CheckoutController.checkout(parsed);
        return res.status(201).json({ msg: 'Sucesso', enrollment_id: result.enrollmentId });
    } catch (err) {
        return res.status(err.status || 500).json({ error: err.message });
    }
});

module.exports = router;
