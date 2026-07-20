const CourseModel      = require('../models/courseModel');
const UserModel        = require('../models/userModel');
const EnrollmentModel  = require('../models/enrollmentModel');
const PaymentModel     = require('../models/paymentModel');
const AuditModel       = require('../models/auditModel');
const { VISA_PREFIX, PAYMENT_STATUS } = require('./constants');
const { ValidationError, NotFoundError, PaymentDeniedError } = require('../errors/domainErrors');

const CheckoutController = {
    async checkout({ userName, email, password, courseId, cardNumber }) {
        const course = await CourseModel.findById(courseId);
        if (!course) throw new NotFoundError('Curso não encontrado');

        let user = await UserModel.findByEmail(email);
        if (!user) {
            if (!password) {
                throw new ValidationError('password é obrigatório para criar uma nova conta');
            }
            const newUserId = await UserModel.create({ name: userName, email, password });
            user = { id: newUserId };
        }

        const paymentStatus = cardNumber.startsWith(VISA_PREFIX)
            ? PAYMENT_STATUS.PAID
            : PAYMENT_STATUS.DENIED;

        if (paymentStatus === PAYMENT_STATUS.DENIED) {
            throw new PaymentDeniedError('Pagamento recusado');
        }

        const enrollmentId = await EnrollmentModel.create({ userId: user.id, courseId });
        await PaymentModel.create({ enrollmentId, amount: course.price, status: paymentStatus });
        await AuditModel.log(`Checkout curso ${courseId} por usuario ${user.id}`);

        return { enrollmentId };
    },
};

module.exports = CheckoutController;
