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
import click


import templgen
from templgen.templgen import Templgen

# from templgen.settings import Settings
# from templgen.template_processor import TemplateProcessor
from iotanbo_py_utils import file_utils


@click.group()
def main():
    pass


@main.command()
def update():
    tg = Templgen()
    tg.ensure_integrity()
    tg._settings.update_settings_for_path(file_utils.get_user_home_dir())
    print(tg._settings._parser.items('GENERAL'))


@main.command()
@click.argument('names', nargs=-1)
def get(names):
    tg = Templgen()
    tg.ensure_integrity()
    tg._settings.update_settings_for_path(file_utils.get_user_home_dir())
    for name in names:
        print(f"{tg._settings.get(name)[0]}")

# @click.command()
# @click.argument("update", default="")
#
# @click.argument("get", default="")
# @click.option("-t", "--template", default="",
#               help="Specify template name, e.g. '-t cppclassfile'")
# @click.option("-c", "--classnames", default="",
#               help="Specify comma-separated C++ class names for C++ templates, e.g. -c 'MyClass1,MyClass2'")
# # @click.argument('names', nargs=-1)
# @click.version_option()
# def main(*, update, template, classnames):
#     # click.echo(repr(names))
#     # if 'version' in names:
#     #     print(f"templgen version {templgen.__version__}")
#     #     exit(0)
#     tg = Templgen()
#     tg.ensure_integrity()
#     if update:
#         tg._settings.update_settings_for_path(file_utils.get_user_home_dir())
#     if template:
#         print(f"Selected template: {template}")
#     if classnames:
#         class_names = classnames.split(',')
#         print(f"Selected class names: {class_names}")
