import re
from abc import ABCMeta, abstractmethod
from typing import Iterator, Mapping, Optional, Pattern

_posix_variable: Pattern[str] = re.compile(
    r"""
    \$\{
        (?P<name>[^\}:+?-]*)
        (?:
            (?P<action_spec>:?[+?-])(?P<argument>[^\}]*)
        )?
    \}
    """,
    re.VERBOSE,
)


class Atom(metaclass=ABCMeta):
    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    @abstractmethod
    def resolve(self, env: Mapping[str, Optional[str]]) -> str: ...


class Literal(Atom):
    def __init__(self, value: str) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"Literal(value={self.value})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash((self.__class__, self.value))

    def resolve(self, env: Mapping[str, Optional[str]]) -> str:
        return self.value


class Action:
    def __init__(self, spec: str, argument: str = ""):
        assert len(spec) > 0
        self.spec = spec
        self.argument = argument

    def __repr__(self) -> str:
        return f"Action(spec={self.spec}, argument={self.argument})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (self.spec, self.argument) == (other.spec, other.argument)

    def __hash__(self) -> int:
        return hash((self.__class__, self.spec, self.argument))

    def resolves_empty(self, value: Optional[str]):
        if value is None:
            return True
        return self.spec[0] == ":" and value == ""

    def resolve(self, name: str, value: Optional[str]):
        empty = self.resolves_empty(value)
        action = self.spec[-1]
        if action == "-" and empty:
            return self.argument
        if action == "+" and not empty:
            return self.argument
        if action == "?" and empty:
            raise LookupError(f"{name}: {self.argument}")
        return value


class Variable(Atom):
    def __init__(self, name: str, action: Optional[Action]) -> None:
        self.name = name
        self.action = action

    def __repr__(self) -> str:
        return f"Variable(name={self.name}, action={repr(self.action)})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (self.name, self.action) == (other.name, other.action)

    def __hash__(self) -> int:
        return hash((self.__class__, self.name, self.action))

    def resolve(self, env: Mapping[str, Optional[str]]) -> str:
        result = env.get(self.name, None)
        if self.action is not None:
            result = self.action.resolve(self.name, result)
        return result if result is not None else ""


def parse_variables(value: str) -> Iterator[Atom]:
    cursor = 0

    for match in _posix_variable.finditer(value):
        (start, end) = match.span()
        name = match["name"]
        action_spec = match["action_spec"]
        argument = match["argument"]
        action = Action(action_spec, argument) if action_spec else None

        if start > cursor:
            yield Literal(value=value[cursor:start])

        yield Variable(name=name, action=action)
        cursor = end

    length = len(value)
    if cursor < length:
        yield Literal(value=value[cursor:length])
