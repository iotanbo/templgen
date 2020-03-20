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

# from templgen.settings import Settings
# from templgen.template_processor import TemplateProcessor


@click.command()
@click.option("-t", "--template", default="",
              help="Specify template name, e.g. '-t cppclassfile'")
@click.option("-c", "--classnames", default="",
              help="Specify comma-separated C++ class names for C++ templates, e.g. -c 'MyClass1,MyClass2'")
@click.argument('names', nargs=-1)
def main(names, *, template, classnames):
    # click.echo(repr(names))
    if 'version' in names:
        print(f"templgen version {templgen.__version__}")
    if template:
        print(f"Selected template: {template}")
    if classnames:
        class_names = classnames.split(',')
        print(f"Selected class names: {class_names}")
