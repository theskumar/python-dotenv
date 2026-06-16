import pytest
import tempfile
import os

from dotenv.variables import Literal, Variable, parse_variables
from dotenv import dotenv_values


@pytest.mark.parametrize(
    "value,expected",
    [
        ("", []),
        ("a", [Literal(value="a")]),
        ("${a}", [Variable(name="a", default=None)]),
        ("${a:-b}", [Variable(name="a", default="b")]),
        (
            "${a}${b}",
            [
                Variable(name="a", default=None),
                Variable(name="b", default=None),
            ],
        ),
        (
            "a${b}c${d}e",
            [
                Literal(value="a"),
                Variable(name="b", default=None),
                Literal(value="c"),
                Variable(name="d", default=None),
                Literal(value="e"),
            ],
        ),
    ],
)
def test_parse_variables(value, expected):
    result = parse_variables(value)
    assert list(result) == expected

def test_variables_simple_interpolation():
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        f.write('BASE=base\nFOO=${BASE}/bar\n')
        f.flush()
        values = dotenv_values(f.name)
        assert values == {'BASE': 'base', 'FOO': 'base/bar'}
    os.remove(f.name)

def test_variables_with_default():
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        f.write('FOO=${BAR:-default}\n')
        f.flush()
        values = dotenv_values(f.name)
        assert values == {'FOO': 'default'}
    os.remove(f.name)

def test_variables_escape():
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        f.write('FOO=$${BAR}\n')
        f.flush()
        values = dotenv_values(f.name)
        assert values == {'FOO': '$'}
    os.remove(f.name)
