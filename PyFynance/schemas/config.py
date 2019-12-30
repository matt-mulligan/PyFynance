from marshmallow import Schema, fields, post_load
from schemas.model import Model


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
    test_path = fields.Str(data_key="testPath")

    @post_load
    def create(self, data, **kwargs):
        """
        called by marshmallow package when deserialising completes in order to construct a valid instance.
        :param data:
        :return: None
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
        :return: None
        """

        return Model(**data)


class DatabaseSchema(Schema):
    """
    This class represents the schema of a configuration.database object. Marshmallow uses this class to serialise and
    deserialize python objects to and from json
    """

    db_names = fields.List(fields.String(), data_key="dbNames")
    tables = fields.Dict(keys=fields.Str(), values=fields.List(fields.String()))
    column_specs = fields.Dict(
        keys=fields.Str(),
        values=fields.Dict(keys=fields.Str(), values=fields.Str()),
        data_key="columnSpecs",
    )
    primary_keys = fields.Dict(
        keys=fields.Str(), values=fields.List(fields.String()), data_key="primaryKeys"
    )
    columns = fields.Dict(keys=fields.Str(), values=fields.List(fields.String()))

    @post_load
    def create(self, data, **kwargs):
        """
        called by marshmallow package when deserialising completes in order to construct a valid instance.
        :param data:
        :return: None
        """

        return Model(**data)


class TasksSchema(Schema):
    """
    This class represents the schema of a configuration.database object. Marshmallow uses this class to serialise and
    deserialize python objects to and from json
    """

    load_transactions = fields.Str(data_key="loadTransactions")
    categorize_transactions = fields.Str(data_key="categorizeTransactions")

    @post_load
    def create(self, data, **kwargs):
        """
        called by marshmallow package when deserialising completes in order to construct a valid instance.
        :param data:
        :return: None
        """

        return Model(**data)


class CategorizationEngineOperationsSchema(Schema):
    """
    This class represents the schema of a configuration.database object. Marshmallow uses this class to serialise and
    deserialize python objects to and from json
    """

    contains = fields.Str()
    starts_with = fields.Str(data_key="startsWith")
    ends_with = fields.Str(data_key="endsWith")
    regex = fields.Str()
    multi_contains = fields.Str(data_key="multiContains")

    @post_load
    def create(self, data, **kwargs):
        """
        called by marshmallow package when deserialising completes in order to construct a valid instance.
        :param data:
        :return: None
        """

        return Model(**data)


class CategorizationEngineSchema(Schema):
    """
    This class represents the schema of a configuration.database object. Marshmallow uses this class to serialise and
    deserialize python objects to and from json
    """

    operations = fields.Nested(CategorizationEngineOperationsSchema)

    @post_load
    def create(self, data, **kwargs):
        """
        called by marshmallow package when deserialising completes in order to construct a valid instance.
        :param data:
        :return: None
        """

        return Model(**data)


class ConfigSchema(Schema):
    """
    THis class represents the schema of a configuration object. Marshmallow uses this class to serialise and
    deserialize python objects to and from json
    """

    version = fields.Decimal()
    tasks = fields.Nested(TasksSchema)
    paths = fields.Nested(ConfigPathsSchema)
    ofx_parser = fields.Nested(OFXParserSchema, data_key="ofxParser")
    database = fields.Nested(DatabaseSchema)
    categorization_engine = fields.Nested(
        CategorizationEngineSchema, data_key="categorizationEngine"
    )

    @post_load
    def create(self, data, **kwargs):
        """
        called by marshmallow package when deserialising completes in order to construct a valid instance.
        :param data:
        :return: None
        """

        return Model(**data)
