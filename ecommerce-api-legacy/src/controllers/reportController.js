const ReportModel = require('../models/reportModel');

const ReportController = {
    async getFinancialReport() {
        return ReportModel.getFinancialReport();
    },
};

module.exports = ReportController;
