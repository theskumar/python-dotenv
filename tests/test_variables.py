import pytest

from dotenv.variables import (
    Literal,
    Variable,
    parse_variables,
    set_variable_name_pattern,
)


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
    "value,expected",
    [
        ("", []),
        ("${AB_CD}", [Variable(name="AB_CD", default=None)]),
        ("${A.B.C.D}", [Literal(value="${A.B.C.D}")]),
        ("${a}", [Literal(value="${a}")]),
    ],
)
def test_parse_variables_re(value, expected):
    set_variable_name_pattern(r"""[A-Z0-9_]+""")
    result = parse_variables(value)

    assert list(result) == expected
    set_variable_name_pattern(None)
