import os
from pkg_resources import resource_string
from string import Template

from schemas.config import ConfigSchema


class Configuration(object):
    """
    The configuration module handles the loading and management of all configuration code and values within PyFynance.
    all setup is run for this module off of the __init__ call, which will return you a fully configured python object
    that you can get configuration values off of using dot notation

    .. code-block:: python

        config = Configuration()
        input_path = config.paths.input_path

    The setting of values on this configuration object are governed by the configuration marshmallow schemas found in
    the schemas.config module, as well as the configuration json from the resources/config module that holds all of
    the actual config values to be loaded.

    """

    def __init__(self):
        """
        Constructor of the configuration service object
        """

        self._config = self._load_config()

    def __getattr__(self, item):
        """
        returns an attribute from the private configuration object

        :param item: the item to return
        :return: the value of the item name passed
        """

        return getattr(self._config, item)

    def _get_repo_base_path(self):
        """
        this method will determine the base path for the PyFynance repository

        :return: the base path to the repository
        """

        full_path = os.path.abspath(__file__)
        path_elements = full_path.split(os.sep)
        return os.sep.join(path_elements[:len(path_elements) - 3])

    def _load_config(self):
        """
        this method will load the configuration information from the appropriate json file and substitute in the
        correct values

        :return: None
        """

        config_resource_string = resource_string("PyFynance.resources.config", "config.json").decode("utf-8")
        config_json = self._substitute_params(config_resource_string)
        return ConfigSchema().loads(config_json.replace("\\", "\\\\"))

    def _substitute_params(self, input_string):
        """
        this method will perform parameter subsitution for all ${PARAM} values within the input string

        :param input_string: the string representing the json configuration information
        :return: json configuration string with values subsituted in
        """

        template = Template(input_string)
        repo_base_path = self._get_repo_base_path()
        return template.substitute(repo_base_path=repo_base_path,
                                   sep=os.sep)

