# python-dotenv

[![Build Status](https://travis-ci.org/theskumar/python-dotenv.svg?branch=master)](https://travis-ci.org/theskumar/python-dotenv) [![PyPI version](https://badge.fury.io/py/python-dotenv.svg)](http://badge.fury.io/py/python-dotenv) [![Downloads](https://pypip.in/download/python-dotenv/badge.svg)](https://pypi.python.org/pypi/python-dotenv/)

Forked from awesome but simpler [django-dotenv](https://github.com/jacobian/django-dotenv).  Removes black magic, makes loading .env in settings.py easier, adds remote .env file management capabilities.  Works as a drop-in replacement for django-dotenv.

[foreman](https://github.com/ddollar/foreman) reads from `.env`. `manage.py`
doesn't. Let's fix that.

[heroku config](https://devcenter.heroku.com/articles/config-vars) Lets you add/delete env variables on your remote server from your local command line.  django-dotenv-rw  when used with fabric lets you do the same ```heroku config:set DJANGO_ENV="PRODUCTION" ``` becomes ```fab config:set,DJANGO_ENV,PRODUCTION```

<!-- MarkdownTOC depth=3-->

- [Installation](#installation)
- [Usage](#usage)
  - [Command-line interface](#command-line-interface)
  - [Loading settings from a `.env` file into your django environment](#loading-settings-from-a-env-file-into-your-django-environment)
  - [Setting remote config](#setting-remote-config)
- [Contributing](#contributing)

<!-- /MarkdownTOC -->


# Installation

```
pip install python-dotenv --upgrade
```

# Usage

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

## Loading settings from a `.env` file into your django environment

Option 1 (suggested):  Near the top of `settings.py`. Add:

```python
import os
import dotenv
PROJECT_PATH = os.path.dirname(os.path.dirname(__file__))
dotenv.load_dotenv(os.path.join(PROJECT_PATH, ".env"))
```

Option 2: If you want your server to set the env variables and only use `dotenv` when you're using `manage.py`: in `manage.py` add:

```python
import dotenv
dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
```

## Setting remote config

This is a first pass, will likely change.

Add a config task to your local fabfile, `dotenv_path` is the location of the absolute path of '.env' on the remote server.
```
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

You can either open an issue or send a pull request.
