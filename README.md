# django-dotenv-rw

Forked from awesome but simpler [django-dotenv](https://github.com/jacobian/django-dotenv).  Removes black magic, makes loading .env in settings.py easier, adds remote .env file management capabilities.  Works as a drop-in replacement for django-dotenv.

[foreman](https://github.com/ddollar/foreman) reads from `.env`. `manage.py`
doesn't. Let's fix that.

[heroku config](https://devcenter.heroku.com/articles/config-vars) Lets you add/delete env variables on your remote server from your local command line.  django-dotenv-rw  when used with fabric lets you do the same ```heroku config:set DJANGO_ENV="PRODUCTION" ``` becomes ```fab config:set,DJANGO_ENV,PRODUCTION```

## Installation

```
pip install git+ssh://git@github.com/tedtieken/django-dotenv-rw.git
```

## Usage: loading settings from a .env file into your django environment

Option 1 (suggested):  Near the top of `settings.py`. Add:

```
import os
import dotenv
PROJECT_PATH = os.path.dirname(os.path.dirname(__file__))
dotenv.load_dotenv(os.path.join(PROJECT_PATH, ".env"))
```

Option 2: If you want your server to set the env variables and only use `dotenv` when you're using `manage.py`: in `manage.py` add:
```
import dotenv
dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
```


## Usage: setting remote config

This is a first pass, will likely change.

Put the `dotenv.py` file in the same folder on your server as the `.env` file and `manage.py`.  Then you can add a config task to your local fabfile:
```
@task
def config(action=None,key=None,value=None):
    command = env.django_path + "dotenv.py "
    command += env.django_path + ".env "
    command += action + " " if action else ""
    command += key + " " if key else ""
    command += value + " " if value else ""
    python(command)

```

Usage is designed to mirror the heroku config api very closely.

Get all your remote config info with `fab config`
```
$ fab config
[...webfactional.com] Executing task 'config'
[...webfactional.com] run: python2.7 /home/me/webapps/myapp/myapp/dotenv.py /home/me/webapps/myapp/myapp/.env 
[...webfactional.com] out: DJANGO_DEBUG="true"
[...webfactional.com] out: DJANGO_ENV="test"
```

Set remote config variables with `fab config:set,[key],[value]`
```
$ fab config:set,hello,world
[...webfactional.com] Executing task 'config'
[...webfactional.com] run: python2.7 /home/me/webapps/myapp/myapp/dotenv.py /home/me/webapps/myapp/myapp/.env set hello world 
[...webfactional.com] out: hello: world
```

Get a single remote config variables with `fab config:get,[key]`
```
$ fab config:get,hello,world
[...webfactional.com] Executing task 'config'
[...webfactional.com] run: python2.7 /home/me/webapps/myapp/myapp/dotenv.py /home/me/webapps/myapp/myapp/.env get hello  
[...webfactional.com] out: hello
[...webfactional.com] out: world
```

Delete a remote config variables with `fab config:unset,[key]`
```
$ fab config:unset,hello
[...webfactional.com] Executing task 'config'
[...webfactional.com] run: python2.7 /home/me/webapps/myapp/myapp/dotenv.py /home/me/webapps/myapp/myapp/.env unset hello  
[...webfactional.com] out: unset hello
```

Thanks entirely to fabric and not one bit to this project, you can chain commands like so`fab config:set,[key1],[value1] config:set,[key2],[value2]`
```
$ fab config:set,hello,world config:set,foo,bar config:set,fizz,buzz
[...webfactional.com] Executing task 'config'
[...webfactional.com] run: python2.7 /home/me/webapps/myapp/myapp/dotenv.py /home/me/webapps/myapp/myapp/.env set hello world 
[...webfactional.com] out: hello: world
[...webfactional.com] Executing task 'config'
[...webfactional.com] run: python2.7 /home/me/webapps/myapp/myapp/dotenv.py /home/me/webapps/myapp/myapp/.env set foo bar 
[...webfactional.com] out: foo: bar
[...webfactional.com] Executing task 'config'
[...webfactional.com] run: python2.7 /home/me/webapps/myapp/myapp/dotenv.py /home/me/webapps/myapp/myapp/.env set fizz buzz 
[...webfactional.com] out: fizz: buzz
```

That's it. Webfaction, or whoever your non-paas host is, is now 1 facor closer to an easy 12 factor app.
