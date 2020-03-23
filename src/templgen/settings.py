"""
Global and local (project - scope) settings
"""

from iotanbo_py_utils import file_utils
import os
import configparser
from typing import Union

# Hardcoded settings
# templgen directory is located in user HOME directory and/or in the project directory
TEMPLGEN_DIR_NAME = ".templgen"
TEMPLGEN_USERS_DIR_NAME = "users"
TEMPLGEN_TEMPL_DIR_NAME = "templates"
TEMPLGEN_TEMPL_CONFIG_DIR_NAME = "templ_config"
TEMPLGEN_CONFIG_FILE_EXTENSION = ".cfg"
TEMPLGEN_CONFIG_FILE_NAME = "main.cfg"


class Settings:
    """
    Methods of this class do not raise exceptions, instead they return a tuple
    (result, error); 'result' may be of any type and 'error' is
    an empty string if success or error message otherwise.
    """
    DEFAULT_SETTINGS = {
        "GENERAL": {
            "current_user***": "Name of currently selected user",
            "current_user": ""
        }

    }

    def __init__(self, *, templgen, **kwargs):
        super().__init__(**kwargs)
        self._current_settings = {}
        self._parser = configparser.ConfigParser(allow_no_value=True)
        # root app templgen
        self._templgen = templgen
        self._global_config_dir = os.path.join(file_utils.get_user_home_dir(), TEMPLGEN_DIR_NAME)
        self._global_config_file = os.path.join(self._global_config_dir, TEMPLGEN_CONFIG_FILE_NAME)

    def ensure_integrity(self, is_global=True, path=None) -> (None, str):
        if is_global:
            path = file_utils.get_user_home_dir()

        # Ensure .templgen directory exists
        path_to_templgen = os.path.join(path, TEMPLGEN_DIR_NAME)
        if not file_utils.dir_exists(path_to_templgen):
            # if not exists, create a new one
            print(f" ** Initializing directory '{path_to_templgen}' ...")
            return self.init(is_global, path)
        # Check config file
        config_file = os.path.join(path_to_templgen, TEMPLGEN_CONFIG_FILE_NAME)
        if not file_utils.file_exists(config_file):
            self._create_default_config_file(config_file)
        # TODO: additional check of file structure
        return None, ""

    @staticmethod
    def has_local_settings(path) -> bool:
        return file_utils.dir_exists(os.path.join(path, TEMPLGEN_DIR_NAME))

    def init(self, is_global=True, path=None) -> (None, str):
        """ Create global or local '.templgen' directory and its contents"""
        if is_global:
            path = file_utils.get_user_home_dir()
        path_to_templgen = os.path.join(path, TEMPLGEN_DIR_NAME)
        if file_utils.dir_exists(path_to_templgen):
            # remove old directory
            file_utils.remove_dir_noexcept(path_to_templgen)

        # Create main dir and 'users' and 'templates' dirs inside it
        Settings._create_dir_or_die(os.path.join(path_to_templgen, TEMPLGEN_USERS_DIR_NAME))
        Settings._create_dir_or_die(os.path.join(path_to_templgen, TEMPLGEN_TEMPL_DIR_NAME))
        # Write default config file
        config_file = os.path.join(path_to_templgen, TEMPLGEN_CONFIG_FILE_NAME)
        self._create_default_config_file(config_file)

        return None, ""

    def update_settings_for_path(self, path) -> (None, str):
        """
        Update self._current_settings according to local settings for 'path' (if any)
        and global settings.
        :param path: path to the directory for which settings are updated; normally
                     it's a current working directory
        :return: error message as the second element of the tuple
        """
        if not file_utils.dir_exists(os.path.join(path, TEMPLGEN_DIR_NAME)):
            return None, f"Path not exists{path}"
        # Load global settings
        self._current_settings = {}
        if not file_utils.dir_exists(os.path.join(path, TEMPLGEN_DIR_NAME)):
            return None, ""

        self._parser.read(self._global_config_file)
        for section in self._parser.sections():  # section, pairs
            # print(f"{section}")
            for key, value in self._parser.items(section):
                if not key.endswith("*"):  # keys with asterisk are considered to be comments
                    self._current_settings[key] = value

        # Check if path-local settings exist
        # Load local settings and override global
        pass

    def get(self, name: str) -> (Union[None, str], str):
        """
        Get a setting with the specified name;
        update_settings_for_path() must be called before if the path was changed;
        :param name: setting name
        :return: (result: str, "") if setting exists or
                (None, "Not exists") otherwise;

        """
        if name in self._current_settings:
            return self._current_settings[name], ""
        else:
            return None, "Not exists"

    @staticmethod
    def _create_dir_or_die(path):
        err = file_utils.create_path_noexcept(path)["error"]
        if err:
            print(f"Error: can't create path '{path}', {err}")
            exit(-1)

    def _create_default_config_file(self, path_to_config_file):
        # Set default values in the config parser
        self._parser.read_dict(self.DEFAULT_SETTINGS)

        # Write settings to file
        with open(path_to_config_file, 'w') as settings_file:
            self._parser.write(settings_file)
