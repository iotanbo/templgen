"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mtemplgen` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``templgen.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``templgen.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
# import click

import click.decorators
# from templgen.settings import Settings
# from templgen.template_processor import TemplateProcessor
from iotanbo_py_utils import file_utils

from templgen.templgen import Templgen


@click.group()
def main():
    """
    Templgen is a template instantiation and creation tool.
    Visit https://github.com/iotanbo/templgen to learn more.
    To get detailed help on each command, run: 'templgen command_name --help'
    """
    pass


"""
@main.command()
@click.argument('names', nargs=-1)
def get(names):
    tg = Templgen()
    tg.ensure_integrity()
    current_dir = file_utils.get_cwd()
    tg.settings.read_settings_for_path(current_dir)
    for name in names:
        print(f"{tg.settings.get(name)[0]}")
"""


@main.command()
def initlocal():
    """
    Create local config in current working dir
    """
    tg = Templgen()
    tg.ensure_integrity()
    current_dir = file_utils.get_cwd()
    result, error = tg.settings.initlocal(current_dir)
    if not error:
        print(f"Success: created local config for directory '{current_dir}'")
    else:
        print(f"Error: {error}")


@main.command()
@click.argument("user_name", default="")
@click.option("--local", is_flag=True,
              help="Create user locally for project in current working dir")
@click.option("-d", "--default", is_flag=True,
              help="Create default user config (no interactive questions)")
def adduser(user_name, local, default):
    """Add new user globally (or locally if --local specified)"""
    if not user_name:
        print(f"Error: user name not specified")
        exit(-1)
    interactive = True
    if default:
        print("default user config selected")
        interactive = False
    tg = Templgen()
    tg.ensure_integrity()
    current_dir = file_utils.get_cwd()
    if local:
        _, error = tg.user_manager.add_user(user_name, local=True,
                                            project_path=current_dir,
                                            interactive=interactive)
    else:
        _, error = tg.user_manager.add_user(user_name, local=False,
                                            project_path=None,
                                            interactive=interactive)
    if error:
        print(f"Error: {error}")
    else:
        print(f"Successfully added new user '{user_name}'")


@main.command()
@click.argument("user_name", default="")
@click.option("--local", is_flag=True,
              help="Delete user locally for project in current working dir'")
@click.option("--confirmed", is_flag=True,
              help="No additional confirmation to be performed'")
def deluser(user_name, local, confirmed):
    """Delete user globally (or locally if --local specified)"""
    if not user_name:
        print(f"Error: user name not specified")
        exit(-1)
    if confirmed:
        confirmed = True
    else:
        confirmed = False
    tg = Templgen()
    tg.ensure_integrity()
    current_dir = file_utils.get_cwd()

    if local:
        _, error = tg.user_manager.del_user(user_name, local=True,
                                            project_path=current_dir,
                                            confirmed=confirmed)
    else:
        _, error = tg.user_manager.del_user(user_name, local=False,
                                            project_path=None,
                                            confirmed=confirmed)
    if error:
        if error == "canceled":
            print("Operation canceled")
        else:
            print(f"Error: {error}")
    else:
        print(f"Successfully deleted user '{user_name}'")


def _list_users():
    tg = Templgen()
    tg.ensure_integrity()
    current_dir = file_utils.get_cwd()
    global_user_list = tg.user_manager.list_users(project_path=None)
    local_user_list = tg.user_manager.list_users(project_path=current_dir)

    if not global_user_list:
        if not local_user_list:
            print(f"No users found")
        else:
            print(f"No global users found")
    else:
        print(f"Global users: {global_user_list!r}")
    if local_user_list:
        print(f"Local users: {local_user_list!r}")
    _, error = tg.settings.read_settings_for_path(current_dir)
    if error:
        print(f"Error while reading settings for {current_dir}: {error}")
        exit(0)
    current_user, error = tg.settings.get("current_user")
    if error:
        print(f"Error while getting current user: {error}")
        exit(0)
    print(f"Current user: {current_user}")


@main.command()
def list_users():
    """
    List global, local users and show current user
    """
    _list_users()


@main.command()
def listusers():
    """
    Alias for 'list-users'
    """
    _list_users()


@main.command()
@click.argument("user_name", default="")
@click.option("--local", is_flag=True,
              help="Switch user for current project")
def swuser(user_name, local):
    """
    Switch user globally (or locally if --local specified)
    """
    if not user_name:
        print("Error: user name not specified. Example: 'templgen swuser your_name [--local]'")
        exit(0)
    tg = Templgen()
    tg.ensure_integrity()
    project_path = None
    if local:
        project_path = file_utils.get_cwd()
        if not tg.settings.has_local_settings(project_path):
            print(f"Error: local config for '{project_path}' does not exist. Use 'templgen initlocal' to create one.")
            exit(0)
    _, error = tg.user_manager.switch_user(user_name, project_path=project_path)
    if error:
        print(f"Error: {error}")
        exit(0)
    print(f"Successfully switched user to '{user_name}'")


@main.command()
@click.argument("user_name", default="")
@click.option("--local", is_flag=True,
              help="Local user only")
def edit_user(user_name, local):
    """
    Edit global user (or local if --local specified)
    """
    if not user_name:
        print("Error: user name not specified. Example: 'templgen edit-user some_user [--local]'")
        exit(0)
    tg = Templgen()
    tg.ensure_integrity()
    project_path = None
    if local:
        project_path = file_utils.get_cwd()
    _, error = tg.user_manager.edit_user(user_name, project_path=project_path)
    if error:
        print(f"Error: {error}")


@main.command()
@click.option("--local", is_flag=True,
              help="Edit local configuration")
def edit_config(local):
    """
    Edit global configuration (or local if --local specified)
    """
    tg = Templgen()
    tg.ensure_integrity()
    project_path = None
    if local:
        project_path = file_utils.get_cwd()
        if not tg.settings.has_local_settings(project_path):
            print(f"Error: local config for '{project_path}' does not exist. Use 'templgen initlocal' to create one.")
            exit(0)
    _, error = tg.settings.edit_config(project_path=project_path)
    if error:
        print(f"Error: {error}")
