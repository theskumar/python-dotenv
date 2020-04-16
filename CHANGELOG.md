# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

*No unreleased change at this time.*

## [0.13.0] - 2020-04-16

### Added

- Add support for a Bash-like default value in variable expansion (#248 by [@bbc2]).

## [0.12.0] - 2020-02-28

### Changed

- Use current working directory to find `.env` when bundled by PyInstaller (#213 by
  [@gergelyk]).

### Fixed

- Fix escaping of quoted values written by `set_key` (#236 by [@bbc2]).
- Fix `dotenv run` crashing on environment variables without values (#237 by [@yannham]).
- Remove warning when last line is empty (#238 by [@bbc2]).

## [0.11.0] - 2020-02-07

### Added

- Add `interpolate` argument to `load_dotenv` and `dotenv_values` to disable interpolation
  (#232 by [@ulyssessouza]).

### Changed

- Use logging instead of warnings (#231 by [@bbc2]).

### Fixed

- Fix installation in non-UTF-8 environments (#225 by [@altendky]).
- Fix PyPI classifiers (#228 by [@bbc2]).

## [0.10.5] - 2020-01-19

### Fixed

- Fix handling of malformed lines and lines without a value (#222 by [@bbc2]):
  - Don't print warning when key has no value.
  - Reject more malformed lines (e.g. "A: B", "a='b',c").
- Fix handling of lines with just a comment (#224 by [@bbc2]).

## [0.10.4] - 2020-01-17

### Added

- Make typing optional (#179 by [@techalchemy]).
- Print a warning on malformed line (#211 by [@bbc2]).
- Support keys without a value (#220 by [@ulyssessouza]).

## 0.10.3

- Improve interactive mode detection ([@andrewsmith])([#183]).
- Refactor parser to fix parsing inconsistencies ([@bbc2])([#170]).
  - Interpret escapes as control characters only in double-quoted strings.
  - Interpret `#` as start of comment only if preceded by whitespace.

## 0.10.2

- Add type hints and expose them to users ([@qnighy])([#172])
- `load_dotenv` and `dotenv_values` now accept an `encoding` parameter, defaults to `None`
  ([@theskumar])([@earlbread])([#161])
- Fix `str`/`unicode` inconsistency in Python 2: values are always `str` now. ([@bbc2])([#121])
- Fix Unicode error in Python 2, introduced in 0.10.0. ([@bbc2])([#176])

## 0.10.1
- Fix parsing of variable without a value ([@asyncee])([@bbc2])([#158])

## 0.10.0

- Add support for UTF-8 in unquoted values ([@bbc2])([#148])
- Add support for trailing comments ([@bbc2])([#148])
- Add backslashes support in values ([@bbc2])([#148])
- Add support for newlines in values ([@bbc2])([#148])
- Force environment variables to str with Python2 on Windows ([@greyli])
- Drop Python 3.3 support ([@greyli])
- Fix stderr/-out/-in redirection ([@venthur])


## 0.9.0

- Add `--version` parameter to cli ([@venthur])
- Enable loading from current directory ([@cjauvin])
- Add 'dotenv run' command for calling arbitrary shell script with .env ([@venthur])

## 0.8.1

-   Add tests for docs ([@Flimm])
-   Make 'cli' support optional. Use `pip install python-dotenv[cli]`. ([@theskumar])

## 0.8.0

-   `set_key` and `unset_key` only modified the affected file instead of
    parsing and re-writing file, this causes comments and other file
    entact as it is.
-   Add support for `export` prefix in the line.
-   Internal refractoring ([@theskumar])
-   Allow `load_dotenv` and `dotenv_values` to work with `StringIO())` ([@alanjds])([@theskumar])([#78])

## 0.7.1

-   Remove hard dependency on iPython ([@theskumar])

## 0.7.0

-   Add support to override system environment variable via .env.
    ([@milonimrod](https://github.com/milonimrod))
    ([\#63](https://github.com/theskumar/python-dotenv/issues/63))
-   Disable ".env not found" warning by default
    ([@maxkoryukov](https://github.com/maxkoryukov))
    ([\#57](https://github.com/theskumar/python-dotenv/issues/57))

## 0.6.5

-   Add support for special characters `\`.
    ([@pjona](https://github.com/pjona))
    ([\#60](https://github.com/theskumar/python-dotenv/issues/60))

## 0.6.4

-   Fix issue with single quotes ([@Flimm])
    ([\#52](https://github.com/theskumar/python-dotenv/issues/52))

## 0.6.3

-   Handle unicode exception in setup.py
    ([\#46](https://github.com/theskumar/python-dotenv/issues/46))

## 0.6.2

-   Fix dotenv list command ([@ticosax](https://github.com/ticosax))
-   Add iPython Suport
    ([@tillahoffmann](https://github.com/tillahoffmann))

## 0.6.0

-   Drop support for Python 2.6
-   Handle escaped charaters and newlines in quoted values. (Thanks
    [@iameugenejo](https://github.com/iameugenejo))
-   Remove any spaces around unquoted key/value. (Thanks
    [@paulochf](https://github.com/paulochf))
-   Added POSIX variable expansion. (Thanks
    [@hugochinchilla](https://github.com/hugochinchilla))

## 0.5.1

-   Fix find\_dotenv - it now start search from the file where this
    function is called from.

## 0.5.0

-   Add `find_dotenv` method that will try to find a `.env` file.
    (Thanks [@isms](https://github.com/isms))

## 0.4.0

-   cli: Added `-q/--quote` option to control the behaviour of quotes
    around values in `.env`. (Thanks
    [@hugochinchilla](https://github.com/hugochinchilla)).
-   Improved test coverage.

[#78]: https://github.com/theskumar/python-dotenv/issues/78
[#121]: https://github.com/theskumar/python-dotenv/issues/121
[#148]: https://github.com/theskumar/python-dotenv/issues/148
[#158]: https://github.com/theskumar/python-dotenv/issues/158
[#170]: https://github.com/theskumar/python-dotenv/issues/170
[#172]: https://github.com/theskumar/python-dotenv/issues/172
[#176]: https://github.com/theskumar/python-dotenv/issues/176
[#183]: https://github.com/theskumar/python-dotenv/issues/183

[@Flimm]: https://github.com/Flimm
[@alanjds]: https://github.com/alanjds
[@altendky]: https://github.com/altendky
[@andrewsmith]: https://github.com/andrewsmith
[@asyncee]: https://github.com/asyncee
[@bbc2]: https://github.com/bbc2
[@cjauvin]: https://github.com/cjauvin
[@earlbread]: https://github.com/earlbread
[@gergelyk]: https://github.com/gergelyk
[@greyli]: https://github.com/greyli
[@qnighy]: https://github.com/qnighy
[@techalchemy]: https://github.com/techalchemy
[@theskumar]: https://github.com/theskumar
[@ulyssessouza]: https://github.com/ulyssessouza
[@venthur]: https://github.com/venthur
[@yannham]: https://github.com/yannham

[Unreleased]: https://github.com/theskumar/python-dotenv/compare/v0.13.0...HEAD
[0.13.0]: https://github.com/theskumar/python-dotenv/compare/v0.12.0...v0.13.0
[0.12.0]: https://github.com/theskumar/python-dotenv/compare/v0.11.0...v0.12.0
[0.11.0]: https://github.com/theskumar/python-dotenv/compare/v0.10.5...v0.11.0
[0.10.5]: https://github.com/theskumar/python-dotenv/compare/v0.10.4...v0.10.5
[0.10.4]: https://github.com/theskumar/python-dotenv/compare/v0.10.3...v0.10.4
