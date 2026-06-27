const { Router } = require('express');
const ReportController = require('../controllers/reportController');

const router = Router();

router.get('/admin/financial-report', async (req, res) => {
    try {
        const report = await ReportController.getFinancialReport();
        return res.status(200).json(report);
    } catch (err) {
        return res.status(500).json({ error: 'Erro ao gerar relatório financeiro' });
    }
});

module.exports = router;
