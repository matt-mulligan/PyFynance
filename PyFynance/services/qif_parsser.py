from core.exceptions import QIFParserError


class QIFParser:
    """
    The QIF Parser class is designed to parse input data in the form of QIF files.
    QIF is a standardised finance information exchange format that PyFynance accepts as an input
    This class can be used to parse the QIF file inputs into python objects utilising marshmallow schemas
    this class is intended as an reusable API class
    """

    def __init__(self, config):
        """
        initialises a new instance of the QIFParser class
        """

        self._config = config

    def parse(self, object_type, path):
        """
        this public method will parse a QIF file from the provided path with the schemas matching the obejct type
        value provided

        :param object_type: the type of objects to parse from the QIF file ["transactions"]
        :param path: the path to the input file

        :return: a python object containing all of the parsed QIF data
        """

        self._check_object_type(object_type)
        self._check_input_file_exists(path)

    def _check_object_type(self, object_type):
        """
        checks that the object_type value provided is part of the acceptable range
        :param object_type: the object_type value to check
        :return:
        """

        if object_type not in self._config.qif_parser.object_types:
            raise QIFParserError("Object_type value '{}' is unknown. "
                                 "Acceptable object type values are '{}'".format(object_type,
                                                                                 self._config.qif_parser.object_types))

    def _check_input_file_exists(self, path):
        """
        this method will check that the path given to the parser exists and is a file object
        :param path:
        :return:
        """
        pass
