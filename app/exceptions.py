"""Domain exceptions for the automated assessment engine."""


class AssessmentError(Exception):
    """Base class for assessment errors."""


class AssessmentNotFoundError(AssessmentError):
    pass


class AssessmentVersionError(AssessmentError):
    pass


class UnknownQuestionError(AssessmentError):
    pass


class InvalidAnswerError(AssessmentError):
    pass


class MaximumAttemptsExceededError(AssessmentError):
    pass


class InvalidScoringPolicyError(AssessmentError):
    pass


class GradingError(AssessmentError):
    pass


class AuditError(AssessmentError):
    pass


class LateSubmissionRejectedError(AssessmentError):
    pass
