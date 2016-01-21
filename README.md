# django-dotenv

[![Build Status](https://travis-ci.org/jpadilla/django-dotenv.svg)](https://travis-ci.org/jpadilla/django-dotenv)
[![PyPI Version](https://pypip.in/version/django-dotenv/badge.svg)](https://pypi.python.org/pypi/django-dotenv)

[foreman](https://github.com/ddollar/foreman) reads from `.env`. `manage.py`
doesn't. Let's fix that.

Tested on Python 2.6, 2.7, 3.2, 3.3, and 3.4.

## Installation

```
pip install django-dotenv
```

## Usage

Pop open `manage.py`. Add:

```
import dotenv
dotenv.read_dotenv()
```

You can also pass `read_dotenv()` an explicit path to the .env file, or to the directory where it lives. It's smart, it'll figure it out.

### Production

In production environment, you might not need `manage.py` to run your application server. In that case, you need to put the code on `wsgi.py` like this:

```
import os

from django.core.wsgi import get_wsgi_application

import dotenv
dotenv.read_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test.settings")

application = get_wsgi_application()

```

That's it. Now go 12 factor the crap out of something.
