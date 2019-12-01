from marshmallow import Schema, fields, post_load
from schemas.model import Model


class TransactionSchema(Schema):
    """
    This class represents the schema of a Pyfynance rules object. Marshmallow uses this class to serialise and
    deserialize python objects to and from json
    """

    institution = fields.Str()
    account = fields.Str()
    tran_id = fields.Str()
    tran_type = fields.Str()
    amount = fields.Decimal()
    narrative = fields.Str()
    date_posted = fields.Str()
    date_processed = fields.Str()
    primary_rule_id = fields.Str(allow_none=True)
    supp_rule_ids = fields.Str(allow_none=True)

    @post_load
    def create(self, data, **kwargs):
        """
        called by marshmallow package when deserialising completes in order to construct a valid instance.
        :param data:
        :return: None
        """

        return Model(**data)
