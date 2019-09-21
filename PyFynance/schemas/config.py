from marshmallow import Schema, fields, post_load
from PyFynance.schemas.model import Model


class ConfigPathsSchema(Schema):
    """
    This class represents the schema of a configuration.paths object. Marshmallow uses this class to serialise and
    deserialize python objects to and from json
    """

    repo_path = fields.Str(data_key="repoPath")
    code_path = fields.Str(data_key="codePath")
    input_path = fields.Str(data_key="inputPath")
    output_path = fields.Str(data_key="outputPath")
    logs_path = fields.Str(data_key="logsPath")
    resources_path = fields.Str(data_key="resourcesPath")
    db_path = fields.Str(data_key="dbPath")

    @post_load
    def create(self, data, **kwargs):
        """
        called by marshmallow package when deserialising completes in order to construct a valid instance.
        :param data:
        :return:
        """

        return Model(**data)


class OFXParserSchema(Schema):
    """
    This class represents the schema of a configuration.qif_parser object. Marshmallow uses this class to serialise and
    deserialize python objects to and from json
    """

    object_types = fields.List(fields.String(), data_key="objectTypes")
    cast_fields = fields.List(fields.String(), data_key="castFields")
    html_tags = fields.List(fields.String(), data_key="htmlTags")

    @post_load
    def create(self, data, **kwargs):
        """
        called by marshmallow package when deserialising completes in order to construct a valid instance.
        :param data:
        :return:
        """

        return Model(**data)


class ConfigSchema(Schema):
    """
    THis class represents the schema of a configuration object. Marshmallow uses this class to serialise and
    deserialize python objects to and from json
    """

    version = fields.Decimal()
    paths = fields.Nested(ConfigPathsSchema)
    ofx_parser = fields.Nested(OFXParserSchema, data_key="ofxParser")

    @post_load
    def create(self, data, **kwargs):
        """
        called by marshmallow package when deserialising completes in order to construct a valid instance.
        :param data:
        :return:
        """

        return Model(**data)
