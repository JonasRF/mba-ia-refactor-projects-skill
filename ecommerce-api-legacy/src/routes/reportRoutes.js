const { Router } = require('express');
const ReportController = require('../controllers/reportController');
const { requireAdmin } = require('../middleware/authMiddleware');
const { HTTP_STATUS } = require('../constants/httpStatus');

const router = Router();

router.get('/admin/financial-report', requireAdmin, async (req, res, next) => {
    try {
        const report = await ReportController.getFinancialReport();
        return res.status(HTTP_STATUS.OK).json(report);
    } catch (err) {
        return next(err);
    }
});

module.exports = router;
