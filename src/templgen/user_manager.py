"""

"""
import configparser
import os
from typing import Union

from iotanbo_py_utils import file_utils

from templgen.settings import Settings

# Type aliases
ErrorMsg = str
StringOrNone = Union[str, None]


class UserManager:
    DEFAULT_USER_CONFIG = [
        # ("param_name", "default_value", "section_name", "description")
        ("full_name", "", "GENERAL", "User full name: "),
        ("email", "", "GENERAL", "Email: "),
        ("site", "", "GENERAL", "Personal site: ")
    ]

    def __init__(self, templgen, **kwargs):
        super().__init__(**kwargs)
        self._templgen = templgen
        self.home_dir = file_utils.get_user_home_dir()
        self.global_templgen_dir = self._templgen.settings.global_templgen_dir
        self.cfg_parser = configparser.ConfigParser(allow_no_value=True)

    # def ensure_integrity(self, path=None) -> (None, ErrorMsg):
    #     if not path:
    #         path = file_utils.get_user_home_dir()
    #
    #     # Ensure .templgen directory exists
    #     path_to_templgen = os.path.join(path, TEMPLGEN_DIR_NAME)
    #     if not file_utils.dir_exists(path_to_templgen):
    #         # if not exists, create a new one
    #         print(f" ** Initializing directory '{path_to_templgen}' ...")
    #         return self.init(is_global, path)
    #     # Check config file
    #     config_file = os.path.join(path_to_templgen, TEMPLGEN_CONFIG_FILE_NAME)
    #     if not file_utils.file_exists(config_file):
    #         self._create_default_config_file(config_file)
    #     # TODO: additional check of file structure
    #     return None, ""

    def add_user(self, user_name: str, local=False,
                 project_path: StringOrNone = None,
                 interactive=True) -> (None, ErrorMsg):
        """
        Add (create) new user globally or locally
        :param user_name: user name to be added
        :param local: if True, user will be added only to project scope
        :param project_path: path to project directory or None if user to be added globally
        :param interactive: if True, user will be asked questions, otherwise
                            default config params will be used
        :return: (None, ErrorMsg) - Error message if error, empty string otherwise
        """
        if local:
            # Ensure settings integrity for project_path
            result, error = self._templgen.settings.ensure_integrity(project_path)
            if error:
                return None, error
        else:
            project_path = file_utils.get_user_home_dir()

        # Check if user exists
        if self.user_exists(user_name, project_path):
            # If exists, return with error
            return None, f"user '{user_name}' already exists"

        # Get information about user
        if interactive:
            user_config_dict = self._get_interactive_user_config(user_name)
        else:
            user_config_dict = self._get_default_user_config(user_name)

        # Create dir for user
        user_dir = os.path.join(project_path, Settings.TEMPLGEN_DIR_NAME,
                                Settings.TEMPLGEN_USERS_DIR_NAME, user_name)

        error = file_utils.create_path_noexcept(user_dir)["error"]
        if error:
            return None, error

        # Create templ_config dir
        user_templ_config_dir = os.path.join(user_dir,
                                             Settings.TEMPLGEN_USER_TEMPL_CONFIG_DIR_NAME)
        error = file_utils.create_path_noexcept(user_templ_config_dir)["error"]
        if error:
            return None, error

        # Write user config file
        config_file = os.path.join(user_dir, Settings.TEMPLGEN_USER_CONFIG_FILE_NAME)
        return Settings.update_config_file(self.cfg_parser, config_file, user_config_dict)
        # self._update_user_config_file(config_file, user_config_dict)

    def del_user(self, user_name: str, local=False,
                 project_path: StringOrNone = None,
                 confirmed=False) -> (None, ErrorMsg):
        """
        Delete existing user globally or locally
        :param user_name: user name to be deleted
        :param local: if True, user will be deleted only from project scope
        :param project_path: path to project directory or None if user has to be deleted globally
        :param confirmed: if False, additional interactive confirmation will be performed
        :return: (None, ErrorMsg) - Error message if any, empty string if success
        """
        if local:
            # Ensure settings integrity for project_path
            result, error = self._templgen.settings.ensure_integrity(project_path)
            if error:
                return None, error
        else:
            project_path = file_utils.get_user_home_dir()

        # Check if user exists
        if not self.user_exists(user_name, project_path):
            # If exists, return with error
            return None, f"user '{user_name}' not exists"

        # Confirm if not yet confirmed

        if not confirmed:
            if local:
                prompt = f"Do you confirm deleting user '{user_name}' locally for '{project_path}' (yes/no)?"
            else:
                prompt = f"Do you confirm deleting user '{user_name}' globally (yes/no)?"
            confirm = input(prompt)
            if "yes" != confirm:
                return None, "canceled"
        # delete user folder
        user_dir = os.path.join(project_path, Settings.TEMPLGEN_DIR_NAME,
                                Settings.TEMPLGEN_USERS_DIR_NAME, user_name)
        error = file_utils.remove_dir_noexcept(user_dir)["error"]
        if error:
            return None, error

        return None, ""

    @staticmethod
    def list_users(project_path: StringOrNone) -> list:
        """
        Lists users for the specified path
        :param project_path: project for which users will be listed;
                             if none, global users will be listed;
        :return: list of user names
        """
        if not project_path:
            project_path = file_utils.get_user_home_dir()

        users_dir = os.path.join(project_path,
                                 Settings.TEMPLGEN_DIR_NAME,
                                 Settings.TEMPLGEN_USERS_DIR_NAME)
        # print(f"debug userlist users_dir: {users_dir}")
        if not file_utils.dir_exists(users_dir):
            return []
        error = file_utils.get_subdirs(users_dir)["error"]
        if error:
            return []

        return file_utils.get_subdirs(users_dir)["subdirs"]

    def edit_user(self, user_name, project_path=None) -> (None, ErrorMsg):
        settings = self._templgen.settings
        settings.read_settings_for_path(project_path)
        if not user_name:
            user_name = self._templgen.settings.get("current_user")
        if not project_path:
            project_path = file_utils.get_user_home_dir()
        if not self.user_exists(user_name, project_path):
            return None, "user not exists"
        text_editor, error = self._templgen.settings.get("text_editor")
        if error:
            text_editor = "nano"
        user_config_file = os.path.join(project_path, Settings.TEMPLGEN_DIR_NAME,
                                        Settings.TEMPLGEN_USERS_DIR_NAME,
                                        user_name,
                                        Settings.TEMPLGEN_USER_CONFIG_FILE_NAME)
        # Execute shell command
        cmd = [text_editor, user_config_file]
        Settings.execute_shell_cmd(cmd)
        return None, ""

    def switch_user(self, user_name, project_path=None) -> (None, ErrorMsg):
        """
        Switch user for the current project or globally if user not found locally.
        :param user_name:
        :param project_path: Path to the project; if project does not contain local .templgen dir,
                             user will be switched globally
        :return: Error message as the second element of the tuple
        """
        # Create alias for the settings
        settings = self._templgen.settings
        if not user_name:
            return None, "invalid user name"
        # is_local = True
        # Ensure that project_path is valid
        if not project_path:
            project_path = file_utils.get_user_home_dir()
            # is_local = False
        # Read local settings for the path
        settings.read_settings_for_path(project_path)

        # Check if user exists for the project path:
        if not UserManager.user_exists(user_name, project_path):
            return None, "user not found"

        # Write new user to the settings
        # TODO
        return settings.set("current_user", user_name)

    # def _update_user_config_file(self, config_file, new_values: dict) -> None:
    #     """
    #     Read user config file if exists, update it with values, save back to file
    #     :param config_file:
    #     :param new_values: dict with following struct: {
    #                                                     "section1": {"key1": "val1", "key2": "val2, ...},
    #                                                     ...
    #                                                     }
    #     :return: None
    #     """
    #     result = {}
    #     # Read current user config from file
    #     if file_utils.file_exists(config_file):
    #         self.cfg_parser.read(config_file)
    #         # Convert it into a dictionary
    #         result = Settings.config_parser_to_dict(self.cfg_parser)
    #         print(f"debug: config file exists: {config_file}")
    #
    #     # Update result with new values
    #     for section, section_entries in new_values.items():
    #         if section not in result:
    #             result[section] = {}
    #             for key, value in section_entries.items():
    #                 result[section][key] = value
    #     # Convert dictionary back into configparser
    #     self.cfg_parser.read_dict(result)
    #
    #     # Write settings to file
    #     with open(config_file, 'w') as f:
    #         self.cfg_parser.write(f)

    # @staticmethod
    # def _config_parser_to_dict(cfg_parser) -> dict:
    #     result = {}
    #     for section in cfg_parser.sections():
    #         section_entries = {}
    #         for key, value in cfg_parser.items(section):
    #             section_entries[key] = value
    #         result[section] = section_entries
    #     return result

    @staticmethod
    def user_exists(user_name, project_path) -> bool:
        """
        Check if user exists for the project ( either locally or globally)
        """
        return (UserManager.user_exists_locally(user_name, project_path) or
                UserManager.user_exists_globally(user_name))

    @staticmethod
    def user_exists_locally(user_name, project_path) -> bool:
        """
        Check if user exists for the project (both
        :param user_name:
        :param project_path:
        :return:
        """
        user_dir = os.path.join(project_path, Settings.TEMPLGEN_DIR_NAME,
                                Settings.TEMPLGEN_USERS_DIR_NAME, user_name)
        if file_utils.dir_exists(user_dir):
            return True
        return False

    @staticmethod
    def user_exists_globally(user_name) -> bool:
        """
        Check if user exists globally
        """
        user_dir = os.path.join(file_utils.get_user_home_dir(), Settings.TEMPLGEN_DIR_NAME,
                                Settings.TEMPLGEN_USERS_DIR_NAME, user_name)
        # print(f"Debug: user_dir: {user_dir}")
        if file_utils.dir_exists(user_dir):
            return True
        return False

    @staticmethod
    def _get_default_user_config(_) -> dict:  # user_name
        result = {}
        for param, value, section, desc in UserManager.DEFAULT_USER_CONFIG:
            if section not in result:
                result[section] = {}
            result[section][param] = value
            return result

    @staticmethod
    def _get_interactive_user_config(_) -> dict:  # user_name
        result = {}
        for param, value, section, desc in UserManager.DEFAULT_USER_CONFIG:
            # print(desc)
            # val = sys.stdin.readline()
            val = input(desc)
            if section not in result:
                result[section] = {}
            result[section][param] = val
        return result
