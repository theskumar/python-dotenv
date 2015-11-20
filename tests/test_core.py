import warnings

from dotenv import load_dotenv


def test_warns_if_file_does_not_exist():
    with warnings.catch_warnings(record=True) as w:
        load_dotenv('.does_not_exist')

        assert len(w) == 1
        assert w[0].category is UserWarning
        assert str(w[0].message) == "Not loading .does_not_exist - it doesn't exist."
