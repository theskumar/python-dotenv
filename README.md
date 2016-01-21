# django-dotenv

[![build-status-image]][travis]
[![pypi-version]][pypi]

[foreman][foreman] reads from `.env`. `manage.py` doesn't. Let's fix that.

Original implementation was written by [@jacobian][jacobian].

Tested on Python 2.7, 3.3, 3.4, and 3.5.

## Installation

```
pip install django-dotenv
```

## Usage

Your `manage.py` should look like:

```python
#!/usr/bin/env python
import os
import sys

import dotenv


if __name__ == "__main__":
    dotenv.read_dotenv()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
```

You can also pass `read_dotenv()` an explicit path to the `.env` file, or to the directory where it lives. It's smart, it'll figure it out.

Check out [tests.py][tests-py] to see all the supported formats that your `.env` can have.

### Using with WSGI

If you're running Django with WSGI and want to load a `.env` file, your `wsgi.py` would look like this:

```python
import os

import dotenv
from django.core.wsgi import get_wsgi_application

dotenv.read_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

application = get_wsgi_application()
```

That's it. Now go 12 factor the crap out of something.

[build-status-image]: https://travis-ci.org/jpadilla/django-dotenv.svg
[travis]: https://travis-ci.org/jpadilla/django-dotenv
[pypi-version]: https://img.shields.io/pypi/v/django-dotenv.svg
[pypi]: https://pypi.python.org/pypi/django-dotenv
[foreman]: https://github.com/ddollar/foreman
[jacobian]: https://github.com/jacobian
[tests-py]: https://github.com/jpadilla/django-dotenv/blob/master/tests.py
