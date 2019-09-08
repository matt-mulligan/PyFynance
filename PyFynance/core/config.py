import os
from pkg_resources import resource_string
from string import Template

from schemas.config import ConfigSchema


class Configuration(object):
    def __init__(self):
        """
        Constructor of the configuration service object
        """

        self._config = self._load_config()

    def __getattr__(self, item):
        """
        returns an attribute from the private configuration object
        :param item:
        :return:
        """

        return getattr(self._config, item)

    def _get_repo_base_path(self):
        """
        this method will determine the base path for the PyFynance repository
        :return:
        """

        full_path = os.path.abspath(__file__)
        path_elements = full_path.split(os.sep)
        return os.sep.join(path_elements[:len(path_elements) - 3])

    def _load_config(self):
        """
        this method will load the configuration information from the appropriate json file and substitute in the
        correct values
        :return:
        """

        config_resource_string = resource_string("PyFynance.resources.config", "config.json").decode("utf-8")
        config_json = self._substitute_params(config_resource_string)
        return ConfigSchema().loads(config_json.replace("\\", "\\\\"))

    def _substitute_params(self, input_string):
        """
        this method will perform parameter subsitution for all ${PARAM} values within the input string
        :param input_string:
        :return:
        """

        template = Template(input_string)
        repo_base_path = self._get_repo_base_path()
        return template.substitute(repo_base_path=repo_base_path,
                                   sep=os.sep)

