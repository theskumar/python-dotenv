```
        _______ .__   __. ____    ____
       |   ____||  \ |  | \   \  /   /
       |  |__   |   \|  |  \   \/   /
       |   __|  |  . `  |   \      /
    __ |  |____ |  |\   |    \    /
   (__)|_______||__| \__|     \__/
```
python-dotenv | [![Build Status](https://travis-ci.org/theskumar/python-dotenv.svg?branch=master)](https://travis-ci.org/theskumar/python-dotenv) [![Coverage Status](https://coveralls.io/repos/theskumar/python-dotenv/badge.svg?branch=master)](https://coveralls.io/r/theskumar/python-dotenv?branch=master) [![PyPI version](https://badge.fury.io/py/python-dotenv.svg)](http://badge.fury.io/py/python-dotenv) [![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/theskumar)
===============================================================================

Reads the key,value pair from `.env` file and adds them to environment
variable. It is great for managing app settings during development and
in production using [12-factor](http://12factor.net/) principles.

> Do one thing, do it well!

- [Usages](#usages)
- [Installation](#installation)
- [Command-line interface](#command-line-interface)
- [iPython Support](#ipython-support)
- [Setting config on remote servers](#setting-config-on-remote-servers)
- [Related Projects](#related-projects)
- [Contributing](#contributing)
- [Changelog](#changelog)

> Hey just wanted to let you know that since I've started writing 12-factor apps I've found python-dotenv to be invaluable for all my projects. It's super useful and “just works.” --Daniel Fridkin

Usages
======

The easiest and most common usage consists on calling `load_dotenv` when
the application starts, which will load environment variables from a
file named `.env` in the current directory or any of its parents or from
the path specificied; after that, you can just call the
environment-related method you need as provided by `os.getenv`.

`.env` looks like this:

```shell
# a comment and that will be ignored.
REDIS_ADDRESS=localhost:6379
MEANING_OF_LIFE=42
MULTILINE_VAR="hello\nworld"
```

You can optionally prefix each line with the word `export`, which is totally ignore by this library, but might allow you to [`source`](https://bash.cyberciti.biz/guide/Source_command) the file in bash.

```
export S3_BUCKET=YOURS3BUCKET
export SECRET_KEY=YOURSECRETKEYGOESHERE
```

`.env` can interpolate variables using POSIX variable expansion,
variables are replaced from the environment first or from other values
in the `.env` file if the variable is not present in the environment.
(`Note`: Default Value Expansion is not supported as of yet, see
[\#30](https://github.com/theskumar/python-dotenv/pull/30#issuecomment-244036604).)

```shell
CONFIG_PATH=${HOME}/.config/foo
DOMAIN=example.org
EMAIL=admin@${DOMAIN}
```

Getting started
===============

Assuming you have created the `.env` file along-side your settings
module.

    .
    ├── .env
    └── settings.py

Add the following code to your `settings.py`

```python
# settings.py
from dotenv import load_dotenv
load_dotenv()

# OR, the same with increased verbosity:
load_dotenv(verbose=True)

# OR, explicitly providing path to '.env'
from pathlib import Path  # python3 only
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
```

At this point, parsed key/value from the .env file is now present as
system environment variable and they can be conveniently accessed via
`os.getenv()`

```python
# settings.py
import os
SECRET_KEY = os.getenv("EMAIL")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
```

`load_dotenv` do not override existing System environment variables. To
override, pass `override=True` to `load_dotenv()`.

`load_dotenv` also accepts `encoding` parameter to open the `.env` file. The default encoding is platform dependent (whatever `locale.getpreferredencoding()` returns), but any encoding supported by Python can be used. See the [codecs](https://docs.python.org/3/library/codecs.html#standard-encodings) module for the list of supported encodings.

You can use `find_dotenv()` method that will try to find a `.env` file
by (a) guessing where to start using `__file__` or the working directory
-- allowing this to work in non-file contexts such as IPython notebooks
and the REPL, and then (b) walking up the directory tree looking for the
specified file -- called `.env` by default.

```python
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
```

In-memory filelikes
-------------------

It is possible to not rely on the filesystem to parse filelikes from
other sources (e.g. from a network storage). `load_dotenv` and
`dotenv_values` accepts a filelike `stream`. Just be sure to rewind it
before passing.

```python
>>> from io import StringIO     # Python2: from StringIO import StringIO
>>> from dotenv import dotenv_values
>>> filelike = StringIO('SPAM=EGGS\n')
>>> filelike.seek(0)
>>> parsed = dotenv_values(stream=filelike)
>>> parsed['SPAM']
'EGGS'
```

The returned value is dictionary with key value pair.

`dotenv_values` could be useful if you need to *consume* the envfile but
not *apply* it directly into the system environment.

Django
------

If you are using django you should add the above loader script at the
top of `wsgi.py` and `manage.py`.

Installation
============

    pip install -U python-dotenv

iPython Support
---------------

You can use dotenv with iPython. You can either let the dotenv search
for .env with %dotenv or provide the path to .env file explicitly, see
below for usages.

    %load_ext dotenv

    # Use find_dotenv to locate the file
    %dotenv

    # Specify a particular file
    %dotenv relative/or/absolute/path/to/.env

    # Use '-o' to indicate override of existing variables
    %dotenv -o

    # Use '-v' to turn verbose mode on
    %dotenv -v

Command-line interface
======================

For commandline support, use the cli option during installation:

    pip install -U "python-dotenv[cli]"

A cli interface `dotenv` is also included, which helps you manipulate
the `.env` file without manually opening it. The same cli installed on
remote machine combined with fabric (discussed later) will enable you to
update your settings on remote server, handy isn't it!

```
Usage: dotenv [OPTIONS] COMMAND [ARGS]...

  This script is used to set, get or unset values from a .env file.

Options:
  -f, --file PATH                 Location of the .env file, defaults to .env
                                  file in current working directory.
  -q, --quote [always|never|auto]
                                  Whether to quote or not the variable values.
                                  Default mode is always. This does not affect
                                  parsing.
  --help                          Show this message and exit.

Commands:
  get    Retrive the value for the given key.
  list   Display all the stored key/value.
  run    Run command with environment variables from .env file present
  set    Store the given key/value.
  unset  Removes the given key.
```

Setting config on remote servers
--------------------------------

We make use of excellent [Fabric](http://www.fabfile.org/) to acomplish
this. Add a config task to your local fabfile, `dotenv_path` is the
location of the absolute path of `.env` file on the remote server.

```python
# fabfile.py

import dotenv
from fabric.api import task, run, env

# absolute path to the location of .env on remote server.
env.dotenv_path = '/opt/myapp/.env'

@task
def config(action=None, key=None, value=None):
    '''Manage project configuration via .env

    e.g: fab config:set,<key>,<value>
         fab config:get,<key>
         fab config:unset,<key>
         fab config:list
    '''
    run('touch %(dotenv_path)s' % env)
    command = dotenv.get_cli_string(env.dotenv_path, action, key, value)
    run(command)
```

Usage is designed to mirror the heroku config api very closely.

Get all your remote config info with `fab config`

    $ fab config
    foo="bar"

Set remote config variables with `fab config:set,<key>,<value>`

    $ fab config:set,hello,world

Get a single remote config variables with `fab config:get,<key>`

    $ fab config:get,hello

Delete a remote config variables with `fab config:unset,<key>`

    $ fab config:unset,hello

Thanks entirely to fabric and not one bit to this project, you can chain
commands like so
`fab config:set,<key1>,<value1> config:set,<key2>,<value2>`

    $ fab config:set,hello,world config:set,foo,bar config:set,fizz=buzz

Related Projects
================

-   [Honcho](https://github.com/nickstenning/honcho) - For managing
    Procfile-based applications.
-   [django-dotenv](https://github.com/jpadilla/django-dotenv)
-   [django-environ](https://github.com/joke2k/django-environ)
-   [django-configuration](https://github.com/jezdez/django-configurations)
-   [dump-env](https://github.com/sobolevn/dump-env)
-   [environs](https://github.com/sloria/environs)

Contributing
============

All the contributions are welcome! Please open [an
issue](https://github.com/theskumar/python-dotenv/issues/new) or send us
a pull request.

This project is currently maintained by [Saurabh Kumar](https://saurabh-kumar.com) and [Bertrand Bonnefoy-Claudet](https://github.com/bbc2) and would not
have been possible without the support of these [awesome
people](https://github.com/theskumar/python-dotenv/graphs/contributors).

Executing the tests:

    $ pip install -r requirements.txt
    $ pip install -e .
    $ flake8
    $ pytest

or with [tox](https://pypi.org/project/tox/) installed:

    $ tox

Changelog
=========

Unreleased
-----

- ...


0.10.2
-----

- Add type hints and expose them to users ([@qnighy])([#172])
- `load_dotenv` and `dotenv_values` now accept an `encoding` parameter, defaults to `None`
  ([@theskumar])([@earlbread])([#161])
- Fix `str`/`unicode` inconsistency in Python 2: values are always `str` now. ([@bbc2])([#121])
- Fix Unicode error in Python 2, introduced in 0.10.0. ([@bbc2])([#176])

0.10.1
-----
- Fix parsing of variable without a value ([@asyncee])([@bbc2])([#158])

0.10.0
-----

- Add support for UTF-8 in unquoted values ([@bbc2])([#148])
- Add support for trailing comments ([@bbc2])([#148])
- Add backslashes support in values ([@bbc2])([#148])
- Add support for newlines in values ([@bbc2])([#148])
- Force environment variables to str with Python2 on Windows ([@greyli])
- Drop Python 3.3 support ([@greyli])
- Fix stderr/-out/-in redirection ([@venthur])


0.9.0
-----
- Add `--version` parameter to cli ([@venthur])
- Enable loading from current directory ([@cjauvin])
- Add 'dotenv run' command for calling arbitrary shell script with .env ([@venthur])

0.8.1
-----

-   Add tests for docs ([@Flimm])
-   Make 'cli' support optional. Use `pip install python-dotenv[cli]`. ([@theskumar])

0.8.0
-----

-   `set_key` and `unset_key` only modified the affected file instead of
    parsing and re-writing file, this causes comments and other file
    entact as it is.
-   Add support for `export` prefix in the line.
-   Internal refractoring ([@theskumar])
-   Allow `load_dotenv` and `dotenv_values` to work with `StringIO())` ([@alanjds])([@theskumar])([#78])

0.7.1
-----

-   Remove hard dependency on iPython ([@theskumar])

0.7.0
-----

-   Add support to override system environment variable via .env.
    ([@milonimrod](https://github.com/milonimrod))
    ([\#63](https://github.com/theskumar/python-dotenv/issues/63))
-   Disable ".env not found" warning by default
    ([@maxkoryukov](https://github.com/maxkoryukov))
    ([\#57](https://github.com/theskumar/python-dotenv/issues/57))

0.6.5
-----

-   Add support for special characters `\`.
    ([@pjona](https://github.com/pjona))
    ([\#60](https://github.com/theskumar/python-dotenv/issues/60))

0.6.4
-----

-   Fix issue with single quotes ([@Flimm])
    ([\#52](https://github.com/theskumar/python-dotenv/issues/52))

0.6.3
-----

-   Handle unicode exception in setup.py
    ([\#46](https://github.com/theskumar/python-dotenv/issues/46))

0.6.2
-----

-   Fix dotenv list command ([@ticosax](https://github.com/ticosax))
-   Add iPython Suport
    ([@tillahoffmann](https://github.com/tillahoffmann))

0.6.0
-----

-   Drop support for Python 2.6
-   Handle escaped charaters and newlines in quoted values. (Thanks
    [@iameugenejo](https://github.com/iameugenejo))
-   Remove any spaces around unquoted key/value. (Thanks
    [@paulochf](https://github.com/paulochf))
-   Added POSIX variable expansion. (Thanks
    [@hugochinchilla](https://github.com/hugochinchilla))

0.5.1
-----

-   Fix find\_dotenv - it now start search from the file where this
    function is called from.

0.5.0
-----

-   Add `find_dotenv` method that will try to find a `.env` file.
    (Thanks [@isms](https://github.com/isms))

0.4.0
-----

-   cli: Added `-q/--quote` option to control the behaviour of quotes
    around values in `.env`. (Thanks
    [@hugochinchilla](https://github.com/hugochinchilla)).
-   Improved test coverage.

[#161]: https://github.com/theskumar/python-dotenv/issues/161
[#78]: https://github.com/theskumar/python-dotenv/issues/78
[#148]: https://github.com/theskumar/python-dotenv/issues/148
[#158]: https://github.com/theskumar/python-dotenv/issues/158
[#172]: https://github.com/theskumar/python-dotenv/issues/172
[#121]: https://github.com/theskumar/python-dotenv/issues/121
[#176]: https://github.com/theskumar/python-dotenv/issues/176

[@asyncee]: https://github.com/asyncee
[@greyli]: https://github.com/greyli
[@venthur]: https://github.com/venthur
[@Flimm]: https://github.com/Flimm
[@theskumar]: https://github.com/theskumar
[@alanjds]: https://github.com/alanjds
[@cjauvin]: https://github.com/cjauvin
[@bbc2]: https://github.com/bbc2
[@qnighy]: https://github.com/qnighy
[@earlbread]: https://github.com/earlbread
