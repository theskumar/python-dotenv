import pytest

from dotenv.variables import Literal, Variable, Action, parse_variables


@pytest.mark.parametrize(
    "value,expected",
    [
        ("", []),
        ("a", [Literal(value="a")]),
        ("${a}", [Variable(name="a", action=None)]),

        ("${a:-b}", [Variable(name="a", action=Action(":-","b"))]),
        ("${a-b}", [Variable(name="a", action=Action("-","b"))]),

        ("${a:+b}", [Variable(name="a", action=Action(":+","b"))]),
        ("${a+b}", [Variable(name="a", action=Action("+","b"))]),

        ("${a:?b}", [Variable(name="a", action=Action(":?","b"))]),
        ("${a?b}", [Variable(name="a", action=Action("?","b"))]),
        ("${a??b}", [Variable(name="a", action=Action("?","?b"))]),

        # Unsupported
        ("${a:b}", [Literal(value="${a:b}")]),
        ("${a!b}", [Variable(name="a!b", action=None)]),

        (
            "${a}${b}",
            [
                Variable(name="a", action=None),
                Variable(name="b", action=None),
            ],
        ),
        (
            "a${b}c${d}e",
            [
                Literal(value="a"),
                Variable(name="b", action=None),
                Literal(value="c"),
                Variable(name="d", action=None),
                Literal(value="e"),
            ],
        ),
    ]
)
def test_parse_variables(value, expected):
    result = parse_variables(value)

    assert list(result) == expected
