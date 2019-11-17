from marshmallow import Schema, fields, post_load
from schemas.model import Model


class RulesSchema(Schema):
    """
    This class represents the schema of a Pyfynance rules object. Marshmallow uses this class to serialise and
    deserialize python objects to and from json
    """

    id = fields.Str()
    type = fields.Str()
    operation = fields.Str()
    value = fields.Str()
    confidence = fields.Int()
    tran_category = fields.Str()
    primary_category = fields.Str()
    secondary_category = fields.Str()

    @post_load
    def create(self, data, **kwargs):
        """
        called by marshmallow package when deserialising completes in order to construct a valid instance.
        :param data:
        :return: None
        """

        return Model(**data)
