const { dbGet } = require('../database/connection');

const CourseModel = {
    async findById(courseId) {
        const row = await dbGet(
            'SELECT * FROM courses WHERE id = ? AND active = 1',
            [courseId]
        );
        return row ? CourseModel._toDict(row) : null;
    },

    _toDict(row) {
        return {
            id:     row.id,
            title:  row.title,
            price:  row.price,
            active: Boolean(row.active),
        };
    },
};

module.exports = CourseModel;
