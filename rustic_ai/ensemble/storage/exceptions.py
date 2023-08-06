class EnsembleNotFoundError(Exception):
    """
    An exception raised when an ensemble is not found in the storage.
    """

    pass


class EnsembleIdAlreadyExists(Exception):
    """
    An exception raised when an ensemble with a duplicate ID is created in the storage.
    """

    pass


class EnsembleMemberNotFoundError(Exception):
    """
    An exception raised when an ensemble member is not found in the storage.
    """

    pass
