class TaskError(ValueError):
    """
    Represents an error that occurs during the running of a tasks before, do or after task
    """

    pass


class TaskLoadTransactionsError(ValueError):
    """
    Represents an error that occurs during the running of a tasks before, do or after task
    """

    pass


class DatabaseError(ValueError):
    """
    Represents an error that occurs within the Database service
    """

    pass


class OFXParserError(ValueError):
    """
    Represents an error that occurs within the QIFParser service
    """

    pass
