class RegistrableAlreadyExistsError(Exception):
    """Exception raised when a Registrable should be added to a
    Registry, but it already exists in this Registry.
    """

    pass


class RegistrableNotFoundError(Exception):
    """Exception raised when a Registrable is not found in the
    corresponding Registry.
    """

    pass
