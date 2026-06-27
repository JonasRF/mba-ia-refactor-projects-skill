const { dbRun } = require('../database/connection');

const AuditModel = {
    async log(action) {
        await dbRun(
            "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
            [action]
        );
    },
};

module.exports = AuditModel;
