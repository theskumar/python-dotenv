from .cli import get_cli_string
from .main import load_dotenv, get_key, set_key, unset_key, find_dotenv, dotenv_values


__all__ = ['get_cli_string',
           'load_dotenv',
           'dotenv_values',
           'get_key',
           'set_key',
           'unset_key',
           'find_dotenv',
           'load_ipython_extension']


def load_ipython_extension(ipython):
    from .ipython import load_ipython_extension
    load_ipython_extension(ipython)
