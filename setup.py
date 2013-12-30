from setuptools import setup

setup(
    name = "django-dotenv-rw",
    description = ".env file settings for non-heroku setups",
    version = "0.1",
    author = "Ted Tieken",
    author_email = "ted@sittingaround.com",
    url = "http://github.com/tedtieken/django-dotenv-rw",
    py_modules = ['dotenv'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
    ]
)
