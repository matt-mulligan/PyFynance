class Model(object):
    """
    this class represents the base model object and encapsulates data found in any and all model objects using
    named keyword arguments provided by Marshmallow
    """

    def __init__(self, **kwargs):
        """
        constructs a new Model object, generally only called by marshmallow
        :param kwargs:
        """

        for key, value in kwargs.items():
            setattr(self, key, value)
