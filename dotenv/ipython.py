from __future__ import print_function
from .main import load_dotenv, find_dotenv


def _magic(dotenv_path):
    """
    dotenv [dotenv_path]

    Search in increasingly higher folders for the `dotenv_path`
    """
    # Locate the .env file
    dotenv_path = dotenv_path or '.env'
    try:
        dotenv_path = find_dotenv(dotenv_path, True, True)
    except IOError:
        print("cannot find .env file")
        return

    # Load the .env file
    load_dotenv(dotenv_path)


def load_ipython_extension(ipython):
    """Register the %dotenv magic."""
    ipython.register_magic_function(_magic, magic_name='dotenv')
