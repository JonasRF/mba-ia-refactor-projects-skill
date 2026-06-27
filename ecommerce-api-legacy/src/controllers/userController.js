const UserModel = require('../models/userModel');

const UserController = {
    async deleteUser(userId) {
        const changes = await UserModel.delete(userId);
        return { deleted: changes > 0 };
    },
};

module.exports = UserController;
