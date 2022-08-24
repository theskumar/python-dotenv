import re
from abc import ABCMeta
from typing import Iterator, Mapping, Optional, Pattern


class Atom():
    __metaclass__ = ABCMeta

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def resolve(self, env: Mapping[str, Optional[str]]) -> str:
        raise NotImplementedError


class Literal(Atom):
    def __init__(self, value: str) -> None:
        self.value = value

    def __repr__(self) -> str:
        return "Literal(value={})".format(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash((self.__class__, self.value))

    def resolve(self, env: Mapping[str, Optional[str]]) -> str:
        return self.value


class Variable(Atom):
    def __init__(self, name: str, default: Optional[Iterator[Atom]]) -> None:
        self.name = name
        self.default = default

    def __repr__(self) -> str:
        return "Variable(name={}, default={})".format(self.name, self.default)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (self.name, self.default) == (other.name, other.default)

    def __hash__(self) -> int:
        return hash((self.__class__, self.name, self.default))

    def resolve(self, env: Mapping[str, Optional[str]]) -> str:
        # default = self.default if self.default is not None else ""
        default = "".join(atom.resolve(env) for atom in self.default) if self.default is not None else ""
        result = env.get(self.name, default)
        return result if result is not None else ""


_variable_re = re.compile(
    r"""
    ^
        (?P<name>[^\}:]*?)
        (?::[-=]
            (?P<default>.*)
        )?
    $
    """,
    re.VERBOSE,
)  # type: Pattern[str]

ESC_CHAR = '\\'


def parse_variables(value: str) -> Iterator[Atom]:
    cursor = 0

    starts = []
    esc = False
    for i in range(len(value)):
        if esc:
            esc = False
        elif ESC_CHAR == value[i]:
            esc = True
        elif i < len(value) - 1 and '$' == value[i] and '{' == value[i+1]:
            if len(starts) == 0 and cursor < i:
                yield Literal(value=value[cursor:i])
            starts.append(i + 2)
        elif '}' == value[i]:
            start = starts.pop()
            end = i
            cursor = i+1
            if len(starts) == 0:
                for match in _variable_re.finditer(value[start:end]):
                    name = match.groupdict()["name"]
                    default = match.groupdict()["default"]
                    default = None if default is None else list(parse_variables(default))
                    yield Variable(name=name, default=default)

    length = len(value)
    if cursor < length:
        yield Literal(value=value[cursor:length])
