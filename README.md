<pre>
     _______ .__   __. ____    ____
    |   ____||  \ |  | \   \  /   /
    |  |__   |   \|  |  \   \/   /
    |   __|  |  . `  |   \      /
 __ |  |____ |  |\   |    \    /
(__)|_______||__| \__|     \__/
</pre>
# python-dotenv

[![Build Status](https://travis-ci.org/theskumar/python-dotenv.svg?branch=master)](https://travis-ci.org/theskumar/python-dotenv) [![Coverage Status](https://coveralls.io/repos/theskumar/python-dotenv/badge.svg?branch=master)](https://coveralls.io/r/theskumar/python-dotenv?branch=master) [![PyPI version](https://badge.fury.io/py/python-dotenv.svg)](http://badge.fury.io/py/python-dotenv) [![PyPI](https://img.shields.io/pypi/dm/python-dotenv.svg)]()

Reads the key,value pair from `.env` and adds them to environment variable. It is great of managing app settings during development and in production using [12-factor] principles.

> Do one thing, do it well!

<!-- MarkdownTOC -->

- [Usages](#usages)
- [Installation](#installation)
- [Command-line interface](#command-line-interface)
  - [Setting config on remote servers](#setting-config-on-remote-servers)
- [Releated Projects](#releated-projects)
- [Contributing](#contributing)

<!-- /MarkdownTOC -->


[12-factor]: http://12factor.net/

# Usages

`.env` is a simple text file. With each environment variables listed per line, in the format of `KEY="Value"`

<pre>
SECRET_KEY="your_secret_key"
DATABASE_PASSWORD="your_database_password"
...
</pre>

If you want to be really fancy with your env file you can do comments (below is a valid env file)

```shell
# I am a comment and that is OK
SOME_VAR=someval
FOO=BAR
```

Assuming you have created the `.env` file along-side your settings module.
```
.
├── .env
└── settings.py
```

Add the following code to your `settings.py`

```python
# settings.py
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
```

Now, you can access the variables either from existing environment variable or loaded from `.env` file. `.env` file gets higher precedence, and it's adviced not to include it in version control.

```python
# settings.py

SECRET_KEY = os.environ.get("SECRET_KEY")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
```

### Django

If you are using django you should add the above loader script at the top of `wsgi.py` and `manage.py`.


# Installation

```
pip install python-dotenv --upgrade
```


# Command-line interface

A cli interface `dotenv` is also included, which helps you manipulate the `.env` file without manually opening it. The same cli installed on remote machine combined with fabric (discussed later) will enable you to update your settings on remote server, handy isn't it!

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

## Setting config on remote servers

We make use of excellent [Fabric] to accomplish this. Add a config task to your local fabfile, `dotenv_path` is the location of the absolute path of `.env` file on the remote server.

[Fabric]: http://www.fabfile.org/

```python
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

# Releated Projects

- [Honcho](https://github.com/nickstenning/honcho) - For managing Procfile-based applications.
- [django-dotenv](https://github.com/jpadilla/django-dotenv)
- [django-environ](https://github.com/joke2k/django-environ)
- [django-configuration](https://github.com/jezdez/django-configurations)

# Contributing

All the contributions are welcome! Please open [an issue] or send us a pull request.

[an issue]: https://github.com/theskumar/python-dotenv/issues/new
