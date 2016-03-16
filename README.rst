::

        _______ .__   __. ____    ____
       |   ____||  \ |  | \   \  /   /
       |  |__   |   \|  |  \   \/   /
       |   __|  |  . `  |   \      /
    __ |  |____ |  |\   |    \    /
   (__)|_______||__| \__|     \__/


python-dotenv
=============

|Build Status| |Coverage Status| |PyPI version| |PyPI|

Reads the key,value pair from ``.env`` and adds them to environment
variable. It is great of managing app settings during development and in
production using `12-factor <http://12factor.net/>`__ principles.

    Do one thing, do it well!

-  `Usages <#usages>`__
-  `Installation <#installation>`__
-  `Command-line interface <#command-line-interface>`__
-  `Setting config on remote
   servers <#setting-config-on-remote-servers>`__
-  `Releated Projects <#releated-projects>`__
-  `Contributing <#contributing>`__

Usages
======

Assuming you have created the ``.env`` file along-side your settings
module.

::

    .
    ├── .env
    └── settings.py

Add the following code to your ``settings.py``

.. code:: python

    # settings.py
    from os.path import join, dirname
    from dotenv import load_dotenv

    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

Now, you can access the variables either from system environment
variable or loaded from ``.env`` file. **System environment variables
gets higher precedence** and it's advised not to include it in version control.

.. code:: python

    # settings.py

    SECRET_KEY = os.environ.get("SECRET_KEY")
    DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")


``.env`` is a simple text file. With each environment variables listed
per line, in the format of ``KEY="Value"``, lines starting with `#` is
ignored.

.. code:: shell

    SOME_VAR=someval
    # I am a comment and that is OK
    FOO="BAR"

Django
------

If you are using django you should add the above loader script at the
top of ``wsgi.py`` and ``manage.py``.

Installation
============

::

    pip install -U python-dotenv

Command-line interface
======================

A cli interface ``dotenv`` is also included, which helps you manipulate
the ``.env`` file without manually opening it. The same cli installed on
remote machine combined with fabric (discussed later) will enable you to
update your settings on remote server, handy isn't it!

::

    Usage: dotenv [OPTIONS] COMMAND [ARGS]...

      This script is used to set, get or unset values from a .env file.

    Options:
      -f, --file PATH                 Location of the .env file, defaults to .env
                                      file in current working directory.
      -q, --quote [always|never|auto]
                                      Whether to quote or not the variable values.
                                      Default mode is always.
      --help                          Show this message and exit.

    Commands:
      get    Retrive the value for the given key.
      list   Display all the stored key/value.
      set    Store the given key/value.
      unset  Removes the given key.

Setting config on remote servers
--------------------------------

We make use of excellent `Fabric <http://www.fabfile.org/>`__ to
acomplish this. Add a config task to your local fabfile, ``dotenv_path``
is the location of the absolute path of ``.env`` file on the remote
server.

.. code:: python

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

Usage is designed to mirror the heroku config api very closely.

Get all your remote config info with ``fab config``

::

    $ fab config

Set remote config variables with ``fab config:set,<key>,<value>``

::

    $ fab config:set,hello,world

Get a single remote config variables with ``fab config:get,<key>``

::

    $ fab config:get,hello

Delete a remote config variables with ``fab config:unset,<key>``

::

    $ fab config:unset,hello

Thanks entirely to fabric and not one bit to this project, you can chain
commands like so ``fab config:set,<key1>,<value1> config:set,<key2>,<value2>``

::

    $ fab config:set,hello,world config:set,foo,bar config:set,fizz=buzz


Releated Projects
=================

-  `Honcho <https://github.com/nickstenning/honcho>`__ - For managing
   Procfile-based applications.
-  `django-dotenv <https://github.com/jpadilla/django-dotenv>`__
-  `django-environ <https://github.com/joke2k/django-environ>`__
-  `django-configuration <https://github.com/jezdez/django-configurations>`__

Contributing
============

All the contributions are welcome! Please open `an
issue <https://github.com/theskumar/python-dotenv/issues/new>`__ or send
us a pull request.

This project is currently maintained by `Saurabh Kumar <https://saurabh-kumar.com>`__ and
would not have been possible without the support of these `awesome people <https://github.com/theskumar/python-dotenv/graphs/contributors>`__.

Changelog
=========

0.4.0
-----
- cli: Added `-q/--quote` option to control the behaviour of quotes around values in .env. (Thanks `@hugochinchilla`_).
- Improved test coverage.

.. _@hugochinchilla: https://github.com/hugochinchilla

.. |Build Status| image:: https://travis-ci.org/theskumar/python-dotenv.svg?branch=master
   :target: https://travis-ci.org/theskumar/python-dotenv
.. |Coverage Status| image:: https://coveralls.io/repos/theskumar/python-dotenv/badge.svg?branch=master
   :target: https://coveralls.io/r/theskumar/python-dotenv?branch=master
.. |PyPI version| image:: https://badge.fury.io/py/python-dotenv.svg
   :target: http://badge.fury.io/py/python-dotenv
.. |PyPI| image:: https://img.shields.io/pypi/dm/python-dotenv.svg
   :target: http://badge.fury.io/py/python-dotenv
