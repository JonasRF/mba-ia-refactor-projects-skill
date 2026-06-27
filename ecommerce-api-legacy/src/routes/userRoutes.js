const { Router } = require('express');
const UserController = require('../controllers/userController');

const router = Router();

router.delete('/users/:userId', async (req, res) => {
    const userId = parseInt(req.params.userId, 10);
    if (isNaN(userId) || userId <= 0) {
        return res.status(400).json({ error: 'userId deve ser um número inteiro positivo' });
    }

    try {
        const result = await UserController.deleteUser(userId);
        return res.status(200).json({ msg: 'Usuário deletado', deleted: result.deleted });
    } catch (err) {
        return res.status(500).json({ error: 'Erro ao deletar usuário' });
    }
});

module.exports = router;
