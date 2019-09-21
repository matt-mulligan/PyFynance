from marshmallow import Schema, fields, post_load
from PyFynance.schemas.model import Model


class OFXBankingTransactionSchema(Schema):
    """
    This class represents the schema of a configuration.paths object. Marshmallow uses this class to serialise and
    deserialize python objects to and from json
    """

    type = fields.Str(data_key="trntype")
    date_posted = fields.DateTime(data_key="dtposted")
    amount = fields.Decimal(data_key="trnamt")
    fitid = fields.Str()
    name = fields.Str(allow_none=True)
    memo = fields.Str(allow_none=True)

    @post_load
    def create(self, data, **kwargs):
        """
        called by marshmallow package when deserialising completes in order to construct a valid instance.
        :param data:
        :return:
        """

        return Model(**data)
