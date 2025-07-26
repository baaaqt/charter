class CharterError(Exception):
    """Base class for all Charter-related exceptions."""


class BackendError(CharterError):
    """Base class for backend-related exceptions."""


class BackendNotAvailableError(BackendError):
    """Exception raised when a backend is not available."""


class TransformationError(BackendError):
    """Exception raised when a transformation fails."""


class OperationError(CharterError):
    """Exception raised for invalid or unsupported operations."""


class UnsupportedOperationError(OperationError):
    """Exception raised for unsupported operations in a backend."""
