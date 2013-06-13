from setuptools import setup

setup(
    name = "django-dotenv",
    description = "foreman reads from .env. manage.py doesn't. Let's fix that.",
    version = "1.1",
    author = "Jacob Kaplan-Moss",
    author_email = "jacob@jacobian.org",
    url = "http://github.com/jacobian/django-dotenv",
    py_modules = ['dotenv'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
    ]
)
