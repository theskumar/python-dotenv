# -*- coding: utf8 -*-
import os
import pytest
import tempfile
import warnings

from dotenv import load_dotenv, find_dotenv


def test_warns_if_file_does_not_exist():
    with warnings.catch_warnings(record=True) as w:
        load_dotenv('.does_not_exist')

        assert len(w) == 1
        assert w[0].category is UserWarning
        assert str(w[0].message) == "Not loading .does_not_exist - it doesn't exist."


def test_find_dotenv():
    """
    Create a temporary folder structure like the following:

        tmpXiWxa5/
        └── child1
            ├── child2
            │   └── child3
            │       └── child4
            └── .env

    Then try to automatically `find_dotenv` starting in `child4`
    """
    tmpdir = os.path.realpath(tempfile.mkdtemp())

    curr_dir = tmpdir
    dirs = []
    for f in ['child1', 'child2', 'child3', 'child4']:
        curr_dir = os.path.join(curr_dir, f)
        dirs.append(curr_dir)
        os.mkdir(curr_dir)

    child1, child4 = dirs[0], dirs[-1]

    # change the working directory for testing
    os.chdir(child4)

    # try without a .env file and force error
    with pytest.raises(IOError):
        find_dotenv(raise_error_if_not_found=True, usecwd=True)

    # try without a .env file and fail silently
    assert find_dotenv(usecwd=True) == ''

    # now place a .env file a few levels up and make sure it's found
    filename = os.path.join(child1, '.env')
    with open(filename, 'w') as f:
        f.write("TEST=test\n")
    assert find_dotenv(usecwd=True) == filename
