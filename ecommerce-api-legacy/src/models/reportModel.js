const { dbAll } = require('../database/connection');

const ReportModel = {
    async getFinancialReport() {
        const rows = await dbAll(`
            SELECT
                c.id     AS course_id,
                c.title  AS course_title,
                u.name   AS user_name,
                p.amount AS payment_amount,
                p.status AS payment_status
            FROM courses c
            LEFT JOIN enrollments e ON e.course_id = c.id
            LEFT JOIN users u       ON u.id = e.user_id
            LEFT JOIN payments p    ON p.enrollment_id = e.id
            ORDER BY c.id
        `, []);
        return ReportModel._aggregateByCourse(rows);
    },

    _aggregateByCourse(rows) {
        const courseMap = {};
        for (const row of rows) {
            if (!courseMap[row.course_id]) {
                courseMap[row.course_id] = {
                    course:   row.course_title,
                    revenue:  0,
                    students: [],
                };
            }
            if (row.user_name) {
                if (row.payment_status === 'PAID') {
                    courseMap[row.course_id].revenue += row.payment_amount;
                }
                courseMap[row.course_id].students.push({
                    student: row.user_name,
                    paid:    row.payment_amount || 0,
                });
            }
        }
        return Object.values(courseMap);
    },
};

module.exports = ReportModel;
