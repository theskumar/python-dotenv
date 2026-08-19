import pytest

from dotenv.variables import Literal, Variable, parse_variables, resolve_commands


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


@pytest.mark.parametrize(
    "value,env,expected",
    [
        ("plain", {}, "plain"),
        ("$(echo hello)", {}, "hello"),
        ("prefix-$(echo suffix)", {}, "prefix-suffix"),
        ("$(false)", {}, ""),
        ("$(i_do_not_exist_xyz)", {}, ""),
        ("$(echo ${PREFIX})", {"PREFIX": "hi"}, "hi"),
    ],
)
def test_resolve_commands(value, env, expected):
    assert resolve_commands(value, env) == expected


def test_resolve_commands_strips_trailing_newline():
    assert resolve_commands("$(printf 'x\\n')", {}) == "x"
