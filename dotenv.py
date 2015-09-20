# -*- coding: utf-8 -*-

import os
import warnings
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

import click


def load_dotenv(dotenv_path):
    """
    Read a .env file and load into os.environ.
    """
    if not os.path.exists(dotenv_path):
        warnings.warn("can't read %s - it doesn't exist." % dotenv_path)
        return None
    for k, v in parse_dotenv(dotenv_path):
        os.environ.setdefault(k, v)
    return True


def get_key(dotenv_path, key_to_get):
    """
    Gets the value of a given key from the given .env

    If the .env path given doesn't exist, fails
    """
    key_to_get = str(key_to_get)
    if not os.path.exists(dotenv_path):
        warnings.warn("can't read %s - it doesn't exist." % dotenv_path)
        return None
    dotenv_as_dict = OrderedDict(parse_dotenv(dotenv_path))
    if key_to_get in dotenv_as_dict:
        return dotenv_as_dict[key_to_get]
    else:
        warnings.warn("key %s not found in %s." % (key_to_get, dotenv_path))
        return None


def set_key(dotenv_path, key_to_set, value_to_set):
    """
    Adds or Updates a key/value to the given .env

    If the .env path given doesn't exist, fails instead of risking creating
    an orphan .env somewhere in the filesystem
    """
    key_to_set = str(key_to_set)
    value_to_set = str(value_to_set).strip("'").strip('"')
    if not os.path.exists(dotenv_path):
        warnings.warn("can't write to %s - it doesn't exist." % dotenv_path)
        return None, key_to_set, value_to_set
    dotenv_as_dict = OrderedDict(parse_dotenv(dotenv_path))
    dotenv_as_dict[key_to_set] = value_to_set
    success = flatten_and_write(dotenv_path, dotenv_as_dict)
    return success, key_to_set, value_to_set


def unset_key(dotenv_path, key_to_unset):
    """
    Removes a given key from the given .env

    If the .env path given doesn't exist, fails
    If the given key doesn't exist in the .env, fails
    """
    key_to_unset = str(key_to_unset)
    if not os.path.exists(dotenv_path):
        warnings.warn("can't delete from %s - it doesn't exist." % dotenv_path)
        return None, key_to_unset
    dotenv_as_dict = OrderedDict(parse_dotenv(dotenv_path))
    if key_to_unset in dotenv_as_dict:
        dotenv_as_dict.pop(key_to_unset, None)
    else:
        warnings.warn("key %s not removed from %s - key doesn't exist." % (key_to_unset, dotenv_path))
        return None, key_to_unset
    success = flatten_and_write(dotenv_path, dotenv_as_dict)
    return success, key_to_unset


def parse_dotenv(dotenv_path):
    with open(dotenv_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            v = v.strip("'").strip('"')
            yield k, v


def flatten_and_write(dotenv_path, dotenv_as_dict):
    with open(dotenv_path, "w") as f:
        for k, v in dotenv_as_dict.items():
            f.write('%s="%s"\r\n' % (k, v))
    return True


@click.group()
@click.option('-f', '--file', default=os.path.join(os.getcwd(), '.env'),
              type=click.Path(exists=True),
              help="Location of the .env file, defaults to .env file in current working directory.")
@click.pass_context
def cli(ctx, file):
    '''This script is used to set, get or unset values from a .env file.'''
    ctx.obj = {}
    ctx.obj['FILE'] = file

    # Need to investigate if this can actually work or if the scope of the new environ variables
    # Expires when python exits

    # elif action == "load":
    #     success = load_dotenv(file)
    #     if success != None:
    #         click.echo("loaded %s into environment" % file)
    #     else:
    #         exit(1)


@cli.command()
@click.pass_context
def list(ctx):
    '''Display all the stored key/value.'''
    file = ctx.obj['FILE']
    dotenv_as_dict = parse_dotenv(file)
    for k, v in dotenv_as_dict:
        click.echo('%s="%s"' % (k, v))


@cli.command()
@click.pass_context
@click.argument('key', required=True)
@click.argument('value', required=True)
def set(ctx, key, value):
    '''Store the given key/value.'''
    file = ctx.obj['FILE']
    success, key, value = set_key(file, key, value)
    if success:
        click.echo('%s="%s"' % (key, value))
    else:
        exit(1)


@cli.command()
@click.pass_context
@click.argument('key', required=True)
def get(ctx, key):
    '''Retrive the value for the given key.'''
    file = ctx.obj['FILE']
    stored_value = get_key(file, key)
    if stored_value:
        click.echo('%s="%s"' % (key, stored_value))
    else:
        exit(1)


@cli.command()
@click.pass_context
@click.argument('key', required=True)
def unset(ctx, key):
    '''Removes the given key.'''
    file = ctx.obj['FILE']
    success, key = unset_key(file, key)
    if success:
        click.echo("Successfully removed %s" % key)
    else:
        exit(1)


if __name__ == "__main__":
    cli()
