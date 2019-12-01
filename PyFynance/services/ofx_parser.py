import os
from datetime import datetime
from decimal import Decimal

from bs4 import BeautifulSoup

from core.exceptions import OFXParserError
from schemas.ofx_banking_transaction import OFXBankingTransactionSchema


class OFXParser:
    """
    The OFX Parser class is designed to parse input data in the form of OFX/QFX files.

    OFX is a standardised finance information exchange format that PyFynance accepts as an input.

    Currently this parsing API only supports OFX files that meet the following specification:
        * OFX Specification: 1.0.2
        * OFX Object Types: Banking-Transactions (found within chapter 11 of the OFX specification)

    OFX Specifications can be found here for reference: https://www.ofx.net/downloads.html

    This class can be used to parse the ofx file inputs into python objects utilising marshmallow schemas.
    this class is intended as a reusable API class that can be extended to support other OFX specification types and
    versions
    """

    def __init__(self, config):
        """
        initialises a new instance of the ofxParser class
        """

        self._config = config

    def parse(self, ofx_object_type, path):
        """
        This public method will parse a ofx file from the provided path with the methods and schemas matching the
        OFX object type value provided

        :param ofx_object_type: the type of objects to parse from the ofx file. Currently supported values are
               ["banking_transactions"]
        :type ofx_object_type: String
        :param path: The path to the input file
        :type path: String
        :return: a python object containing all of the parsed ofx data
        """

        self._check_object_type(ofx_object_type)
        self._check_input_file(path)

        parse_method = {"banking_transactions": self._parse_banking_transactions}[
            ofx_object_type
        ]

        return parse_method(path)

    def _check_object_type(self, object_type):
        """
        This private method checks that the object_type value provided is part of the acceptable range from the
        config object

        :param object_type: The object_type value to check
        :type object_type: String
        :return: None
        """

        if object_type not in self._config.ofx_parser.object_types:
            raise OFXParserError(
                f"Object_type value '{object_type}' is unknown. "
                f"Acceptable object type values are '{self._config.ofx_parser.object_types}'"
            )

    def _parse_banking_transactions(self, path):
        """
        This private method is responsible for the parsing of transaction type objects from ofx files into python
        objects

        :param path: the validated input path of the ofx file
        :type path: String
        :return: a set of python objects containing transaction information
        """

        raw_trans = self._read_ofx_file(path)
        tran_dictionaries = self._parse_ofx_transactions(raw_trans)
        tran_dictionaries = self._cast_ofx_values(tran_dictionaries)
        transactions = self._load_dictionaries_to_objects(
            "banking_transactions", tran_dictionaries
        )
        return transactions

    def _parse_ofx_transactions(self, ofx_trans):
        """
        This private method will parse ofx "stmttrn" tags into python dictionary obejcts.

        As ofx files are essentially "poorly formatted" xml, many of the tags do not have closing tags, meaning that
        the tag structure is interpreted as very nested and requires more cleaning than normal xml structures

        :param ofx_trans: Beatuiful soup parser output generated from an ofx file using the "html.parser"
        :type ofx_trans: Beautiful Soup Tag Object
        :return: a list of python dictionaries representing the transactions from the ofx file parsed
        """

        transactions = []
        for tran in ofx_trans:
            tran_data = {}
            for tag in tran.find_all():
                tag_name = tag.name
                if tag_name not in self._config.ofx_parser.html_tags:
                    tag_value = self._get_tag_value(tag)
                    tran_data[tag_name] = tag_value
            transactions.append(tran_data)

        return transactions

    def _cast_ofx_values(self, obj_dictionaries):
        """
        This private method will cast the ofx file values to appropriate datatypes

        :param obj_dictionaries: List containing dictionaries of ofx data
        :type obj_dictionaries: List
        :return: obj_dictionaries containing data cast to the correct format
        """

        cast_dictionaries = []
        for obj_dict in obj_dictionaries:
            for key, value in obj_dict.items():
                if key in self._config.ofx_parser.cast_fields:
                    cast_method = {
                        "dtposted": self._cast_str_to_datetime_string,
                        "dtuser": self._cast_str_to_datetime_string,
                        "trnamt": self._cast_str_to_decimal,
                    }[key]

                    obj_dict[key] = cast_method(value)
            cast_dictionaries.append(obj_dict)

        return cast_dictionaries

    @staticmethod
    def _check_input_file(path):
        """
        This private static method checks the validaity of the ofx/qfx filename that has been passed to the parse.

        This method checks that:
            - The path given to the parser exists and is a file
            - The file object is either ".ofx" or ."qfx" type

        :param path: Path to check
        :type path: String
        :return: None
        """

        if not os.path.isfile(path):
            raise OFXParserError(
                f"Path provided '{path}' either does not exist or isnt a file"
            )

        if not (path.lower().endswith(".ofx") or path.lower().endswith(".qfx")):
            raise OFXParserError(f"Path provided '{path}' is not an OFX/QFX file.")

    @staticmethod
    def _read_ofx_file(path):
        """
        This private static method will read in the ofx file from the path specified and break it into individual
        "stmttrn" entries.

        :param path: the system path to the ofx file
        :type path: String
        :return: a list of Beautiful Soup Tag elements
        """

        with open(path) as ofx_file:
            ofx_data = BeautifulSoup(ofx_file, features="html.parser")

        return ofx_data.find_all("stmttrn")

    @staticmethod
    def _get_tag_value(tag):
        """
        This private static method will extract the value from a tag object. As OFX is essentially "poorly formed" XML
        and has many missing end tags, most of the xml parsers avaliable for python either misinterpret the tag values
        or flat out cannot parse it.

        BeautifulSoup is a step ahead of most and will at least parse the values but misinterprets the missing end tags
        for nesting of tags. This means we must write additional tag value parsing logic to deal with this.

        :param tag: BeautifulSoup tag object to parse the value out of
        :type tag: Beautiful Soup Tag Element
        :return: string value for the tag
        """

        return tag.text.split("\n")[0]

    @staticmethod
    def _load_dictionaries_to_objects(object_type, object_dictionaries):
        """
        This private static method will serialise python dictionaries into objects for easier usage/management

        :param object_type: String indicating the type of objects being loaded
        :type object_type: String
        :param object_dictionaries: List of dictionaries containing the object data
        :type object_dictionaries: List[Dictionary]
        :return: List of python objects loaded to using Marshmallow schemas
        """

        schema = {"banking_transactions": OFXBankingTransactionSchema}[object_type]

        serialised_objects = []
        for obj_dict in object_dictionaries:
            serialised_obj = schema().load(obj_dict)
            serialised_objects.append(serialised_obj)

        return serialised_objects

    @staticmethod
    def _cast_str_to_decimal(value):
        """
        This private static method will cast a string to a decimal

        :param value: String value to cast
        :type value: String
        :return: Decimal representation of the string
        """

        return Decimal(value)

    @staticmethod
    def _cast_str_to_datetime_string(value):
        """
        This private static method will cast a string in ofx format to a datetime

        :param value: String value to cast
        :return: Datetime representation of the string
        """

        format_str = "%Y%m%d" if len(value) == 8 else "%Y%m%d%H%M%S"
        return str(datetime.strptime(value, format_str))
