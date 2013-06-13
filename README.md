# django-dotenv

[foreman](https://github.com/ddollar/foreman) reads from `.env`. `manage.py`
doesn't. Let's fix that.

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

You have to pass in `__file__` so that we know where to find the .env file.
You can also pass an explicit path to the .env file, or to the directory
where it lives. It's smart, it'll figure it out.

That's it. Now go 12 factor the crap out of something.
