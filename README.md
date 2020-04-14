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

Reads the key-value pair from `.env` file and adds them to environment
variable. It is great for managing app settings during development and
in production using [12-factor](http://12factor.net/) principles.

> Do one thing, do it well!

## Usages

The easiest and most common usage consists on calling `load_dotenv` when
the application starts, which will load environment variables from a
file named `.env` in the current directory or any of its parents or from
the path specificied; after that, you can just call the
environment-related method you need as provided by `os.getenv`.

`.env` looks like this:

```shell
# a comment that will be ignored.
REDIS_ADDRESS=localhost:6379
MEANING_OF_LIFE=42
MULTILINE_VAR="hello\nworld"
```

You can optionally prefix each line with the word `export`, which is totally ignored by this library, but might allow you to [`source`](https://bash.cyberciti.biz/guide/Source_command) the file in bash.

```
export S3_BUCKET=YOURS3BUCKET
export SECRET_KEY=YOURSECRETKEYGOESHERE
```

Python-dotenv can interpolate variables using POSIX variable expansion.

The value of a variable is the first of the values defined in the following list:

- Value of that variable in the environment.
- Value of that variable in the `.env` file.
- Default value, if provided.
- Empty string.

Ensure that variables are surrounded with `{}` like `${HOME}` as bare 
variables such as `$HOME` are not expanded.

```shell
CONFIG_PATH=${HOME}/.config/foo
DOMAIN=example.org
EMAIL=admin@${DOMAIN}
DEBUG=${DEBUG:-false}
```

## Getting started

Install the latest version with:

```shell
pip install -U python-dotenv
```

Assuming you have created the `.env` file along-side your settings
module.

    .
    ├── .env
    └── settings.py

Add the following code to your `settings.py`:

```python
# settings.py
from dotenv import load_dotenv
load_dotenv()

# OR, the same with increased verbosity
load_dotenv(verbose=True)

# OR, explicitly providing path to '.env'
from pathlib import Path  # python3 only
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
```

At this point, parsed key/value from the `.env` file is now present as
system environment variable and they can be conveniently accessed via
`os.getenv()`:

```python
# settings.py
import os
SECRET_KEY = os.getenv("EMAIL")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
```

`load_dotenv` does not override existing System environment variables. To
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

### In-memory filelikes

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

The returned value is dictionary with key-value pairs.

`dotenv_values` could be useful if you need to *consume* the envfile but
not *apply* it directly into the system environment.

### Django

If you are using Django, you should add the above loader script at the
top of `wsgi.py` and `manage.py`.


## IPython Support

You can use dotenv with IPython. You can either let the dotenv search
for `.env` with `%dotenv` or provide the path to the `.env` file explicitly; see
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


## Command-line Interface

For command-line support, use the CLI option during installation:

```shell
pip install -U "python-dotenv[cli]"
```

A CLI interface `dotenv` is also included, which helps you manipulate
the `.env` file without manually opening it. The same CLI installed on
remote machine combined with fabric (discussed later) will enable you to
update your settings on a remote server; handy, isn't it!

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


### Setting config on Remote Servers

We make use of excellent [Fabric](http://www.fabfile.org/) to accomplish
this. Add a config task to your local fabfile; `dotenv_path` is the
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

Usage is designed to mirror the Heroku config API very closely.

Get all your remote config info with `fab config`:

    $ fab config
    foo="bar"

Set remote config variables with `fab config:set,<key>,<value>`:

    $ fab config:set,hello,world

Get a single remote config variables with `fab config:get,<key>`:

    $ fab config:get,hello

Delete a remote config variables with `fab config:unset,<key>`:

    $ fab config:unset,hello

Thanks entirely to fabric and not one bit to this project, you can chain
commands like so:
`fab config:set,<key1>,<value1> config:set,<key2>,<value2>`

    $ fab config:set,hello,world config:set,foo,bar config:set,fizz=buzz


## Related Projects

-   [Honcho](https://github.com/nickstenning/honcho) - For managing
    Procfile-based applications.
-   [django-dotenv](https://github.com/jpadilla/django-dotenv)
-   [django-environ](https://github.com/joke2k/django-environ)
-   [django-configuration](https://github.com/jezdez/django-configurations)
-   [dump-env](https://github.com/sobolevn/dump-env)
-   [environs](https://github.com/sloria/environs)
-   [dynaconf](https://github.com/rochacbruno/dynaconf)


## Acknowledgements

This project is currently maintained by [Saurabh Kumar](https://saurabh-kumar.com) and [Bertrand Bonnefoy-Claudet](https://github.com/bbc2) and would not
have been possible without the support of these [awesome
people](https://github.com/theskumar/python-dotenv/graphs/contributors).
