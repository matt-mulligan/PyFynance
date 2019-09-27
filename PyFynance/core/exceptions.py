"""
The exceptions module holds all of the exception classes used throughout the application.

Each exception class is used to signify where an exception has occured within the PyFynance application
"""


class TaskError(ValueError):
    """
    Represents an error that occurs during the running of a base task class
    """

    pass


class TaskLoadTransactionsError(ValueError):
    """
    Represents an error that occurs during the running of a load transactions task
    """

    pass


class DatabaseError(ValueError):
    """
    Represents an error that occurs within the Database service
    """

    pass


class OFXParserError(ValueError):
    """
    Represents an error that occurs within the OFXParser service
    """

    pass
