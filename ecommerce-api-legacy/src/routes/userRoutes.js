const { Router } = require('express');
const UserController = require('../controllers/userController');
const { requireAdmin } = require('../middleware/authMiddleware');
const { ValidationError } = require('../errors/domainErrors');
const { HTTP_STATUS } = require('../constants/httpStatus');

const router = Router();

router.delete('/users/:userId', requireAdmin, async (req, res, next) => {
    const userId = parseInt(req.params.userId, 10);
    if (isNaN(userId) || userId <= 0) {
        return next(new ValidationError('userId deve ser um número inteiro positivo'));
    }

    try {
        const result = await UserController.deleteUser(userId);
        return res.status(HTTP_STATUS.OK).json({ msg: 'Usuário deletado', deleted: result.deleted });
    } catch (err) {
        return next(err);
    }
});

module.exports = router;
