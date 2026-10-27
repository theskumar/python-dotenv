import pytest

from dotenv.variables import Literal, Variable, parse_variables


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


def test_variable_resolve_default_on_empty():
    from dotenv.variables import Variable

    v = Variable("a", "default")
    assert v.resolve({}) == "default"
    assert v.resolve({"a": ""}) == "default"
    assert v.resolve({"a": "val"}) == "val"

    # No default: empty stays empty
    v2 = Variable("a", None)
    assert v2.resolve({}) == ""
    assert v2.resolve({"a": ""}) == ""
