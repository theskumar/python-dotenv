# python-dotenv

[![Build Status](https://travis-ci.org/theskumar/python-dotenv.svg?branch=master)](https://travis-ci.org/theskumar/python-dotenv) [![PyPI version](https://badge.fury.io/py/python-dotenv.svg)](http://badge.fury.io/py/python-dotenv) [![Downloads](https://pypip.in/download/python-dotenv/badge.svg)](https://pypi.python.org/pypi/python-dotenv/)

# Features

The original work is based on [django-dotenv](https://github.com/jacobian/django-dotenv) by jacobian. 

- read values from .env file and loads them as environment variable.
- use it any python project not just django. 
- commandline interface to read/write `.env` file on your local and remote servers.


# Installation

```
pip install python-dotenv --upgrade
```

# Usage

## Format
You define your environment variables with a simple key=value list.

<pre>
SECRET_KEY="your_secret_key"
DATABASE_PASSWORD="your_database_password"
...
</pre>

When using django-configurations, the environment variables have a default
preposition DJANGO_ .
This is only true for **default configuration**, which you can overwrite 
with *environ_prefix* and *environ_name* parameters.

<pre>
DJANGO_SECRET_KEY="your_secret_key"
DJANGO_DATABASE_PASSWORD="your_database_password"
...
</pre>

## Command-line interface

<pre>
$ dotenv
Usage: dotenv [OPTIONS] COMMAND [ARGS]...

  This script is used to set, get or unset values from a .env file.

Options:
  -f, --file PATH  Location of the .env file, defaults to .env file in current
                   working directory.
  --help           Show this message and exit.

Commands:
  get    Retrive the value for the given key.
  list   Display all the stored key/value.
  set    Store the given key/value.
  unset  Removes the given key.
</pre>

## Loading variables from a `.env` file into your python project

### Any Python Project

Add the following line at the start of the file, from your program starts:

```python
import dotenv
DOTENV_PATH = "/path/to/.env"
dotenv.load_dotenv(DOTENV_PATH)
```

### Django

If you are using django you should add the above loader script at the top of `settings.py` and `manage.py`. 

NOTE: If you use [django-configurations], support for reading `.env` file is coming soon[1]!

[1] https://github.com/jezdez/django-configurations/commit/01e3f5837f3d0fed215d

[django-configurations]: https://github.com/jezdez/django-configurations


## Setting config on remote servers

We make use of excellent [Fabric] to acomplish this. Add a config task to your local fabfile, `dotenv_path` is the location of the absolute path of `.env` file on the remote server.

[Fabric]: http://www.fabfile.org/

```
# fabfile.py

from fabric.api import task, run, env

# absolute path to the location of .env on remote server
env.dotenv_path = '/home/me/webapps/myapp/myapp/.env'

@task
def config(action=None, key=None, value=None):
    '''Manage project configuration via .env

    see: https://github.com/theskumar/python-dotenv
    e.g: fab config:set,[key],[value]
    '''
    run('touch %(dotenv_path)s' % env)
    command = 'dotenv'
    command += ' -f %s ' % env.dotenv_path
    command += action + " " if action else " "
    command += key + " " if key else " "
    command += value if value else ""
    run(command)
```

Usage is designed to mirror the heroku config api very closely.

Get all your remote config info with `fab config`
```
$ fab config:list
[...example.com] Executing task 'config'
[...example.com] run: dotenv -f /home/me/webapps/myapp/myapp/.env list
[...example.com] out: DJANGO_DEBUG="true"
[...example.com] out: DJANGO_ENV="test"
```

Set remote config variables with `fab config:set,[key],[value]`
```
$ fab config:set,hello,world
[...example.com] Executing task 'config'
[...example.com] run: dotenv -f /home/me/webapps/myapp/myapp/.env set hello world
[...example.com] out: hello="world"
```

Get a single remote config variables with `fab config:get,[key]`
```
$ fab config:get,hello
[...example.com] Executing task 'config'
[...example.com] run: dotenv -f /home/me/webapps/myapp/myapp/.env get hello
[...example.com] out: hello="world"
```

Delete a remote config variables with `fab config:unset,[key]`
```
$ fab config:unset,hello
[...example.com] Executing task 'config'
[...example.com] run: dotenv -f /home/me/webapps/myapp/myapp/.env unset hello
[...example.com] out: unset hello
```

Thanks entirely to fabric and not one bit to this project, you can chain commands like so`fab config:set,[key1],[value1] config:set,[key2],[value2]`
```
$ fab config:set,hello,world config:set,foo,bar config:set,fizz,buzz
[...example.com] Executing task 'config'
[...example.com] run: dotenv -f /home/me/webapps/myapp/myapp/.env set hello world
[...example.com] out: hello="world"
[...example.com] Executing task 'config'
[...example.com] run: dotenv -f /home/me/webapps/myapp/myapp/.env set foo bar
[...example.com] out: foo="bar"
[...example.com] Executing task 'config'
[...example.com] run: dotenv -f /home/me/webapps/myapp/myapp/.env set fizz buzz
[...example.com] out: fizz="buzz"
```

That's it. example.com, or whoever your non-paas host is, is now 1 facor closer to an easy 12 factor app.

# Contributing

Please open [an issue] or send us a pull request.

[an issue]: https://github.com/theskumar/python-dotenv/issues/new
