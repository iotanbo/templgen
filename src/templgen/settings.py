"""
Global and local (project - scope) settings
"""
import os
import subprocess
from configparser import ConfigParser
from typing import Union

from iotanbo_py_utils import file_utils

# Type aliases
ErrorMsg = str
StringOrNone = Union[str, None]


class Settings:
    """
    Methods of this class do not raise exceptions, instead they return a tuple
    (result, error); 'result' may be of any type and 'error' is
    an empty string if success or error message otherwise.
    """
    DEFAULT_SETTINGS = {
        "GENERAL": {
            "current_user*": "Name of currently selected user",
            "current_user": "",
            "text_editor*": "Text editor to use",
            "text_editor": "gedit",
        }

    }

    # Hardcoded settings
    # templgen directory is located in user HOME directory and/or in the project directory
    TEMPLGEN_DIR_NAME = ".templgen"
    TEMPLGEN_USERS_DIR_NAME = "users"
    # Template config dir for each user
    TEMPLGEN_USER_TEMPL_CONFIG_DIR_NAME = "templ_config"
    TEMPLGEN_TEMPL_DIR_NAME = "templates"
    TEMPLGEN_CONFIG_FILE_EXTENSION = ".cfg"
    TEMPLGEN_CONFIG_FILE_NAME = "main.cfg"
    TEMPLGEN_USER_CONFIG_FILE_NAME = "user.cfg"

    def __init__(self, *, templgen, **kwargs):
        super().__init__(**kwargs)
        self.global_templgen_dir = os.path.join(file_utils.get_user_home_dir(),
                                                Settings.TEMPLGEN_DIR_NAME)
        self.global_config_file = os.path.join(self.global_templgen_dir,
                                               Settings.TEMPLGEN_CONFIG_FILE_NAME)

        self.cfg_parser = ConfigParser(allow_no_value=True)
        self._templgen = templgen
        self._current_settings = {}
        self._current_project_path = None
        self._current_settings_modified = False

    def ensure_integrity(self, path=None) -> (None, ErrorMsg):
        """

        :param path: path to dir that must contain templgen settings;
                     if `None`, path is set to user home dir and global
                     settings integrity is checked
        :return: Error message as the second element in tuple
        """
        if not path:
            path = file_utils.get_user_home_dir()

        # Ensure .templgen directory exists
        path_to_templgen = os.path.join(path, Settings.TEMPLGEN_DIR_NAME)
        if not file_utils.dir_exists(path_to_templgen):
            # if not exists, create a new one
            print(f" ** Initializing directory '{path_to_templgen}' ...")
            return self.init(path)
        # Check config file
        config_file = os.path.join(path_to_templgen, Settings.TEMPLGEN_CONFIG_FILE_NAME)
        if not file_utils.file_exists(config_file):
            self._create_default_config_file(config_file)
        # TODO: additional check of file structure
        return None, ""

    @staticmethod
    def has_local_settings(path) -> bool:
        return file_utils.dir_exists(os.path.join(path, Settings.TEMPLGEN_DIR_NAME))

    def init(self, path=None) -> (None, ErrorMsg):
        """ Create global or local '.templgen' directory and its contents;
            If `path` is `None`, global settings in the user home dir will be initialized
        """
        if not path:
            path = file_utils.get_user_home_dir()
        path_to_templgen = os.path.join(path, Settings.TEMPLGEN_DIR_NAME)
        if file_utils.dir_exists(path_to_templgen):
            # remove old directory
            file_utils.remove_dir_noexcept(path_to_templgen)

        # Create main dir and 'users' and 'templates' dirs inside it
        Settings._create_dir_or_die(os.path.join(path_to_templgen, Settings.TEMPLGEN_USERS_DIR_NAME))
        Settings._create_dir_or_die(os.path.join(path_to_templgen, Settings.TEMPLGEN_TEMPL_DIR_NAME))
        # Write default config file
        config_file = os.path.join(path_to_templgen, Settings.TEMPLGEN_CONFIG_FILE_NAME)
        self._create_default_config_file(config_file)

        return None, ""

    def read_settings_for_path(self, project_path) -> (None, ErrorMsg):
        """
        Update self._current_settings according to local settings for 'project_path' (if any)
        and global settings.
        :param project_path: path to the directory for which settings are updated; normally
                     it's a current working directory
        :return: error message as the second element of the tuple
        """
        if self._current_settings_modified:
            return None, f"modified settings not saved"
        if not file_utils.dir_exists(project_path):
            # return None, f"Path not exists{project_path}"
            project_path = file_utils.get_user_home_dir()
        self._current_project_path = project_path
        # Load global settings

        # print(f"Before adding settings from {self.global_config_file}")
        # self._add_settings_from_file(self.global_config_file)
        self._current_settings, error = Settings.read_settings_from_file(self.cfg_parser,
                                                                         self.global_config_file)
        if error:
            return None, error

        if project_path == file_utils.get_user_home_dir():
            return None, ""

        current_templgen_dir = os.path.join(project_path, Settings.TEMPLGEN_DIR_NAME)
        if not file_utils.dir_exists(current_templgen_dir):
            return None, ""

        # Check if path-local settings exist
        local_config_file = os.path.join(current_templgen_dir, Settings.TEMPLGEN_CONFIG_FILE_NAME)
        # print(f"Before adding settings from {config_file}")
        if file_utils.file_exists(local_config_file):
            # Load local settings and override global
            # self._add_settings_from_file(config_file)
            local_settings, error = Settings.read_settings_from_file(self.cfg_parser,
                                                                     local_config_file)
            if error:
                return None, error
            Settings.merge_settings(self._current_settings, local_settings)
        else:
            print(f"-- Settings: local config file not found: '{local_config_file}'")
        return None, ""

    def get(self, name: str, section: str = "GENERAL") -> (str, ErrorMsg):
        """
        Get a setting with the specified name;
        read_settings_for_path() must be called before to update settings for the specified path;
        :param name: setting name
        :param section: section name, defaults to "GENERAL"
        :return: (result: str, "") if setting exists or
                ("", "Not exists") otherwise;

        """
        # print(f"DEBUG: {self._current_settings}")
        if section not in self._current_settings:
            return "", "Section not exists"
        if name in self._current_settings[section]:
            return self._current_settings[section][name], ""
        else:
            return "", "Not exists"

    def set(self, param: str, value: str, section: str = "GENERAL", save=True) -> (None, ErrorMsg):
        """
        Set new parameter value
        :param param: parameter name
        :param value: new value
        :param section: section name, defaults to "GENERAL"
        :param save: if True, config file will be updated immediately
        :return: Tuple with error message as second element
        """
        if not self._current_project_path:
            return None, "'read_settings_for_path()' must be called before changing settings"
        self._current_settings_modified = True
        if section not in self._current_settings:
            self._current_settings[section] = {}
        self._current_settings[section][param] = value
        if save:
            return self.save_config()

    def save_config(self) -> (None, ErrorMsg):
        """
        Save last read and modified config back to file
        :return: Tuple with error message as second element
        """
        # print(f"DEBUG saving config: {self._current_project_path}, {self._current_settings}")
        # Check if there are changes to be saved
        if not self._current_settings_modified:
            return None, ""
        # Check project_path
        if not self._current_project_path:
            return None, "'read_settings_for_path()' must be called before changing settings"

        _, error = Settings.update_config_file(self.cfg_parser,
                                               os.path.join(self._current_project_path,
                                                            Settings.TEMPLGEN_DIR_NAME,
                                                            Settings.TEMPLGEN_CONFIG_FILE_NAME),
                                               self._current_settings)
        if error:
            return None, error
        self._current_settings_modified = False
        return None, ""

    def edit_config(self, project_path=None) -> (None, ErrorMsg):
        self.read_settings_for_path(project_path)
        if not project_path:
            project_path = file_utils.get_user_home_dir()
        text_editor, error = self._templgen.settings.get("text_editor")
        if error:
            text_editor = "nano"
        config_file = os.path.join(project_path, Settings.TEMPLGEN_DIR_NAME,
                                   Settings.TEMPLGEN_CONFIG_FILE_NAME)
        # Execute shell command
        cmd = [text_editor, config_file]
        Settings.execute_shell_cmd(cmd)
        return None, ""

    @staticmethod
    def update_config_file(config_parser: ConfigParser,
                           path_to_config_file: str,
                           new_values: dict) -> (None, ErrorMsg):
        """
        Read config file or create new if not exists, then add new/modified values to it and save back.
        :param config_parser:
        :param path_to_config_file:
        :param new_values: values to be updated,
                            format is: {
                                        "section1": {"key1": "val1", "key2": "val2, ...},
                                        ...
                                        }
        :return: Error message as second element of the tuple
        """
        # print(f"DEBUG: writing config to file: {path_to_config_file}")
        result = {}
        try:
            # Read current user config from file
            if file_utils.file_exists(path_to_config_file):
                config_parser.read(path_to_config_file)
                # Convert it into a dictionary
                result = Settings.config_parser_to_dict(config_parser)

            # Update result with new values
            Settings.merge_settings(result, new_values)

            # Convert dictionary back into configparser
            config_parser.read_dict(result)
            # print(f"DEBUG: new_values: {new_values}")
            # print(f"DEBUG: resulting config: {result}")

            # Write settings to file
            with open(path_to_config_file, 'w') as f:
                config_parser.write(f)
        except Exception as e:
            return None, str(e)
        return None, ""

    def initlocal(self, path) -> (None, ErrorMsg):
        local_config_dir = os.path.join(path, Settings.TEMPLGEN_DIR_NAME)
        if file_utils.dir_exists(local_config_dir):
            return None, f"local config directory already exists: '{local_config_dir}'"
        # Create a copy of global settings for current user only
        file_utils.copy_dir_noexcept(self.global_templgen_dir, local_config_dir)
        return None, ""
        # return self.init(is_global=False, path=path)

    @staticmethod
    def merge_settings(settings: dict, new_values: dict):
        for section, elements in new_values.items():
            if section not in settings:
                settings[section] = {}
            for key, value in elements.items():
                settings[section][key] = value

    @staticmethod
    def _create_dir_or_die(path) -> None:
        err = file_utils.create_path_noexcept(path)["error"]
        if err:
            print(f"Error: can't create path '{path}', {err}")
            exit(-1)

    def _create_default_config_file(self, path_to_config_file) -> None:
        # Set default values in the config parser
        self.cfg_parser.read_dict(self.DEFAULT_SETTINGS)

        # Write settings to file
        with open(path_to_config_file, 'w') as f:
            self.cfg_parser.write(f)

    # def _add_settings_from_file(self, file_name) -> None:
    #     self.cfg_parser.read(file_name)
    #     for section in self.cfg_parser.sections():  # section, pairs
    #         if section not in self._current_settings:
    #             self._current_settings[section] = {}
    #         for key, value in self.cfg_parser.items(section):
    #             # if not key.endswith("*"):  # keys with asterisk are considered to be comments
    #             self._current_settings[key] = value

    @staticmethod
    def read_settings_from_file(config_parser: ConfigParser, file_name) -> (dict, ErrorMsg):
        try:
            config_parser.read(file_name)
        except Exception as e:
            return {}, str(e)
        return Settings.config_parser_to_dict(config_parser), ""

    @staticmethod
    def config_parser_to_dict(cfg_parser) -> dict:
        result = {}
        for section in cfg_parser.sections():
            section_entries = {}
            for key, value in cfg_parser.items(section):
                section_entries[key] = value
            result[section] = section_entries
        return result

    @staticmethod
    def execute_shell_cmd(cmd_and_args):
        subprocess.check_call(cmd_and_args, env=dict(os.environ))
