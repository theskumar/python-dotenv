import codecs
import os
import sys
from pathlib import Path
from subprocess import Popen
from typing import Any, Dict, List, Optional

import click

from .main import dotenv_values, set_key, unset_key
from .version import __version__


def enumerate_env():
    """
    Display a list of all the variables from the .env file.
    """
    file = os.path.join(os.getcwd(), '.env')
    click.echo(file)
    if os.path.exists(file):
        click.echo('In your %s file:' % file)
        for k, v in dotenv_values(file).items():
            click.echo('%s: %s' % (k, v))
    else:
        click.echo('No %s file found.' % file)


@click.group()
@click.option(
    '-f',
    '--file',
    default=os.path.join(os.getcwd(), '.env'),
    type=click.Path(file_okay=True),
    help='The .env file path.',
    required=False
)
@click.option(
    '-q',
    '--quote',
    default='always',
    type=click.Choice(['always', 'never', 'auto']),
    help='Quote the values in the .env file.',
    required=False
)
@click.option(
    '-e',
    '--export',
    default=False,
    type=click.BOOL,
    help='Append the variables to the file in the form export VAR=value.',
    is_flag=True,
    required=False
)
@click.version_option(version=__version__, prog_name='dotenv')
@click.pass_context
def cli(ctx: click.Context, file: str, quote: str, export: bool) -> None:
    """This script is used to set, get or unset values from a .env file."""
    ctx.obj = {}
    ctx.obj['QUOTE'] = quote
    ctx.obj['EXPORT'] = export
    ctx.obj['FILE'] = file


@cli.command()
@click.pass_context
def list(ctx: click.Context) -> None:
    """Display all the stored key/value."""
    file = ctx.obj['FILE']
    if not os.path.isfile(file):
        click.echo("File doesn't exist: %s" % file)
        sys.exit(1)
    dotenv_as_dict = dotenv_values(file)
    for k, v in dotenv_as_dict.items():
        click.echo('%s=%s' % (k, v))


@cli.command()
@click.pass_context
def get(ctx: click.Context, key: str) -> None:
    """Display the stored value."""
    file = ctx.obj['FILE']
    if not os.path.isfile(file):
        click.echo("File doesn't exist: %s" % file)
        sys.exit(1)
    stored_value = dotenv_values(file).get(key)
    if stored_value:
        click.echo(stored_value)
    else:
        click.echo("Key %s not found." % key)
        sys.exit(1)


get.add_argument = click.argument  # type: ignore
get.add_argument('key', required=True)


@cli.command()
@click.pass_context
def set(
    ctx: click.Context,
    key: str,
    value: str,
) -> None:
    """Store a new variable or update an existing variable."""
    file = ctx.obj['FILE']
    quote = ctx.obj['QUOTE']
    export = ctx.obj['EXPORT']
    success, key, value = set_key(file, key, value, quote, export)
    if success:
        click.echo('%s=%s' % (key, value))
    else:
        click.echo("Key %s not set." % key)
        sys.exit(1)


set.add_argument = click.argument  # type: ignore
set.add_argument('key', required=True)
set.add_argument('value', required=True)


@cli.command()
@click.pass_context
def unset(ctx: click.Context, key: str) -> None:
    """Removes a variable."""
    file = ctx.obj['FILE']
    quote = ctx.obj['QUOTE']
    success = unset_key(file, key, quote)
    if success:
        click.echo("Key %s removed." % key)
    else:
        click.echo("Key %s not found." % key)
        sys.exit(1)


unset.add_argument = click.argument  # type: ignore
unset.add_argument('key', required=True)


@cli.command(context_settings={'ignore_unknown_options': True, 'allow_extra_args': True})
@click.pass_context
def run(ctx: click.Context, commandline: List[str]) -> None:
    """Run a command with the environment variables from the .env file."""
    file = ctx.obj['FILE']
    if not os.path.isfile(file):
        click.echo("File doesn't exist: %s" % file)
        sys.exit(1)

    dotenv_as_dict = {
        k: v
        for (k, v) in dotenv_values(file).items()
        if v is not None
    }

    if not commandline:
        click.echo('No command given.')
        sys.exit(1)
    run_command(commandline, dotenv_as_dict)


run.add_argument = click.argument  # type: ignore
run.add_argument('commandline', nargs=-1)


def run_command(command: List[str], env: Dict[str, str]) -> None:
    """Run the command and set the environment variables.

    Parameters
    ----------
    command: List[str]
        The command and its parameters
    env: Dict
        The additional environment variables

    Returns
    -------
    None
        This function does not return any value. It replaces the current process with the new one.

    """
    # copy the current environment variables and add the vales from
    # `env`
    cmd_env = os.environ.copy()
    cmd_env.update(env)

    if sys.platform == "win32":
        # execvpe on Windows returns control immediately
        # rather than once the command has finished.
        try:
            p = Popen(
                command, universal_newlines=True, bufsize=0, shell=False, env=cmd_env
            )
        except FileNotFoundError:
            print(f"Command not found: {command[0]}", file=sys.stderr)
            sys.exit(1)

        _, _ = p.communicate()

        sys.exit(p.returncode)
    else:
        try:
            os.execvpe(command[0], args=command, env=cmd_env)
        except FileNotFoundError:
            print(f"Command not found: {command[0]}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    cli()
