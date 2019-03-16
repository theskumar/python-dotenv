import click
from typing import Any, List

def cli(ctx: click.Context, file: Any, quote: Any) -> None: ...
def list(ctx: click.Context) -> None: ...
def set(ctx: click.Context, key: Any, value: Any) -> None: ...
def get(ctx: click.Context, key: Any) -> None: ...
def unset(ctx: click.Context, key: Any) -> None: ...
def run(ctx: click.Context, commandline: List[str]) -> None: ...