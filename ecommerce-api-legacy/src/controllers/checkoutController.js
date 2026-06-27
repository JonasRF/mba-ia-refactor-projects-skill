const CourseModel      = require('../models/courseModel');
const UserModel        = require('../models/userModel');
const EnrollmentModel  = require('../models/enrollmentModel');
const PaymentModel     = require('../models/paymentModel');
const AuditModel       = require('../models/auditModel');
const { VISA_PREFIX, PAYMENT_STATUS } = require('./constants');

function domainError(message, status) {
    const err = new Error(message);
    err.status = status;
    return err;
}

const CheckoutController = {
    async checkout({ userName, email, password, courseId, cardNumber }) {
        const course = await CourseModel.findById(courseId);
        if (!course) throw domainError('Curso não encontrado', 404);

        let user = await UserModel.findByEmail(email);
        if (!user) {
            const newUserId = await UserModel.create({
                name: userName,
                email,
                password: password || '123456',
            });
            user = { id: newUserId };
        }

        const paymentStatus = cardNumber.startsWith(VISA_PREFIX)
            ? PAYMENT_STATUS.PAID
            : PAYMENT_STATUS.DENIED;

        if (paymentStatus === PAYMENT_STATUS.DENIED) {
            throw domainError('Pagamento recusado', 400);
        }

        const enrollmentId = await EnrollmentModel.create({ userId: user.id, courseId });
        await PaymentModel.create({ enrollmentId, amount: course.price, status: paymentStatus });
        await AuditModel.log(`Checkout curso ${courseId} por usuario ${user.id}`);

        return { enrollmentId };
    },
};

module.exports = CheckoutController;
