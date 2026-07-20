class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = 'ValidationError';
    }
}

class NotFoundError extends Error {
    constructor(message) {
        super(message);
        this.name = 'NotFoundError';
    }
}

class AuthError extends Error {
    constructor(message) {
        super(message);
        this.name = 'AuthError';
    }
}

class ForbiddenError extends Error {
    constructor(message) {
        super(message);
        this.name = 'ForbiddenError';
    }
}

class PaymentDeniedError extends Error {
    constructor(message) {
        super(message);
        this.name = 'PaymentDeniedError';
    }
}

module.exports = { ValidationError, NotFoundError, AuthError, ForbiddenError, PaymentDeniedError };
