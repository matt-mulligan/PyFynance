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
    This class represents the schema of a configuration.ofx_parser object. Marshmallow uses this class to serialise and
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


class DatabaseTablesSchema(Schema):
    """
    This class represents the schema of a configuration.database.tables object. Marshmallow uses this class to
    serialise and deserialize python objects to and from json
    """

    transactions = fields.List(fields.String())
    rules = fields.List(fields.String())

    @post_load
    def create(self, data, **kwargs):
        """
        called by marshmallow package when deserialising completes in order to construct a valid instance.
        :param data:
        :return:
        """

        return Model(**data)


class DatabaseColumnSpecsSchema(Schema):
    """
    This class represents the schema of a configuration.database.column_spec object. Marshmallow uses this class to serialise and
    deserialize python objects to and from json
    """
    transactions = fields.Dict(keys=fields.Str(), values=fields.Str())


class DatabasePrimaryKeysSchema(Schema):
    """
    This class represents the schema of a configuration.database object. Marshmallow uses this class to serialise and
    deserialize python objects to and from json
    """

    transactions = fields.List(fields.String())

    @post_load
    def create(self, data, **kwargs):
        """
        called by marshmallow package when deserialising completes in order to construct a valid instance.
        :param data:
        :return:
        """

        return Model(**data)


class DatabaseSchema(Schema):
    """
    This class represents the schema of a configuration.database object. Marshmallow uses this class to serialise and
    deserialize python objects to and from json
    """

    db_names = fields.List(fields.String(), data_key="dbNames")
    tables = fields.Nested(DatabaseTablesSchema())
    column_specs = fields.Nested(DatabaseColumnSpecsSchema(), data_key="columnSpecs")
    primary_keys = fields.Nested(DatabasePrimaryKeysSchema(), data_key="primaryKeys")

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
    database = fields.Nested(DatabaseSchema)

    @post_load
    def create(self, data, **kwargs):
        """
        called by marshmallow package when deserialising completes in order to construct a valid instance.
        :param data:
        :return:
        """

        return Model(**data)
