# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- ...

## [1.2.2] - 2026-03-01

### Added

- Support for Python 3.14, including the free-threaded (3.14t) build. (#588)

### Changed

- The `dotenv run` command now forwards flags directly to the specified command by [@bbc2] in [#607]
- Improved documentation clarity regarding override behavior and the reference page.
- Updated PyPy support to version 3.11.
- Documentation for FIFO file support.
- Dropped Support for Python 3.9.

### Fixed

- Improved `set_key` and `unset_key` behavior when interacting with symlinks by [@bbc2] in [790c5c0]
- Corrected the license specifier and added missing Python 3.14 classifiers in package metadata by [@JYOuyang] in [#590]

### Breaking Changes

- `dotenv.set_key` and `dotenv.unset_key` used to follow symlinks in some
  situations. This is no longer the case. For that behavior to be restored in
  all cases, `follow_symlinks=True` should be used.

- In the CLI, `set` and `unset` used to follow symlinks in some situations. This
  is no longer the case.

- `dotenv.set_key`, `dotenv.unset_key` and the CLI commands `set` and `unset`
  used to reset the file mode of the modified .env file to `0o600` in some
  situations. This is no longer the case: The original mode of the file is now
  preserved. Is the file needed to be created or wasn't a regular file, mode
  `0o600` is used.

## [1.2.1] - 2025-10-26

- Move more config to `pyproject.toml`, removed `setup.cfg`
- Add support for reading `.env` from FIFOs (Unix) by [@sidharth-sudhir] in [#586]

## [1.2.0] - 2025-10-26

- Upgrade build system to use PEP 517 & PEP 518 to use `build` and `pyproject.toml` by [@EpicWink] in [#583]
- Add support for Python 3.14 by [@23f3001135] in [#579]
- Add support for disabling of `load_dotenv()` using `PYTHON_DOTENV_DISABLED` env var. by [@matthewfranglen] in [#569]

## [1.1.1] - 2025-06-24

### Fixed

- CLI: Ensure `find_dotenv` work reliably on python 3.13 by [@theskumar] in [#563]
- CLI: revert the use of execvpe on Windows by [@wrongontheinternet] in [#566]

## [1.1.0] - 2025-03-25

### Added

- Add support for python 3.13
- Enhance `dotenv run`, switch to `execvpe` for better resource management and signal handling ([#523]) by [@eekstunt]

### Fixed

- `find_dotenv` and `load_dotenv` now correctly looks up at the current directory when running in debugger or pdb ([#553] by [@randomseed42])

### Misc

- Drop support for Python 3.8

## [1.0.1] - 2024-01-23

### Fixed

- Gracefully handle code which has been imported from a zipfile ([#456] by [@samwyma])
- Allow modules using `load_dotenv` to be reloaded when launched in a separate thread ([#497] by [@freddyaboulton])
- Fix file not closed after deletion, handle error in the rewrite function ([#469] by [@Qwerty-133])

### Misc

- Use pathlib.Path in tests ([#466] by [@eumiro])
- Fix year in release date in changelog.md ([#454] by [@jankislinger])
- Use https in README links ([#474] by [@Nicals])

## [1.0.0] - 2023-02-24

### Fixed

- Drop support for python 3.7, add python 3.12-dev (#449 by [@theskumar])
- Handle situations where the cwd does not exist. (#446 by [@jctanner])

## [0.21.1] - 2023-01-21

### Added

- Use Python 3.11 non-beta in CI (#438 by [@bbc2])
- Modernize variables code (#434 by [@Nougat-Waffle])
- Modernize main.py and parser.py code (#435 by [@Nougat-Waffle])
- Improve conciseness of cli.py and **init**.py (#439 by [@Nougat-Waffle])
- Improve error message for `get` and `list` commands when env file can't be opened (#441 by [@bbc2])
- Updated License to align with BSD OSI template (#433 by [@lsmith77])

### Fixed

- Fix Out-of-scope error when "dest" variable is undefined (#413 by [@theGOTOguy])
- Fix IPython test warning about deprecated `magic` (#440 by [@bbc2])
- Fix type hint for dotenv_path var, add StrPath alias (#432 by [@eaf])

## [0.21.0] - 2022-09-03

### Added

- CLI: add support for invocations via 'python -m'. (#395 by [@theskumar])
- `load_dotenv` function now returns `False`. (#388 by [@larsks])
- CLI: add --format= option to list command. (#407 by [@sammck])

### Fixed

- Drop Python 3.5 and 3.6 and upgrade GA (#393 by [@eggplants])
- Use `open` instead of `io.open`. (#389 by [@rabinadk1])
- Improve documentation for variables without a value (#390 by [@bbc2])
- Add `parse_it` to Related Projects (#410 by [@naorlivne])
- Update README.md (#415 by [@harveer07])
- Improve documentation with direct use of MkDocs (#398 by [@bbc2])

## [0.20.0] - 2022-03-24

### Added

- Add `encoding` (`Optional[str]`) parameter to `get_key`, `set_key` and `unset_key`.
  (#379 by [@bbc2])

### Fixed

- Use dict to specify the `entry_points` parameter of `setuptools.setup` (#376 by
  [@mgorny]).
- Don't build universal wheels (#387 by [@bbc2]).

## [0.19.2] - 2021-11-11

### Fixed

- In `set_key`, add missing newline character before new entry if necessary. (#361 by
  [@bbc2])

## [0.19.1] - 2021-08-09

### Added

- Add support for Python 3.10. (#359 by [@theskumar])

## [0.19.0] - 2021-07-24

### Changed

- Require Python 3.5 or a later version. Python 2 and 3.4 are no longer supported. (#341
  by [@bbc2]).

### Added

- The `dotenv_path` argument of `set_key` and `unset_key` now has a type of `Union[str,
os.PathLike]` instead of just `os.PathLike` (#347 by [@bbc2]).
- The `stream` argument of `load_dotenv` and `dotenv_values` can now be a text stream
  (`IO[str]`), which includes values like `io.StringIO("foo")` and `open("file.env",
"r")` (#348 by [@bbc2]).

## [0.18.0] - 2021-06-20

### Changed

- Raise `ValueError` if `quote_mode` isn't one of `always`, `auto` or `never` in
  `set_key` (#330 by [@bbc2]).
- When writing a value to a .env file with `set_key` or `dotenv set <key> <value>` (#330
  by [@bbc2]):
  - Use single quotes instead of double quotes.
  - Don't strip surrounding quotes.
  - In `auto` mode, don't add quotes if the value is only made of alphanumeric characters
    (as determined by `string.isalnum`).

## [0.17.1] - 2021-04-29

### Fixed

- Fixed tests for build environments relying on `PYTHONPATH` (#318 by [@befeleme]).

## [0.17.0] - 2021-04-02

### Changed

- Make `dotenv get <key>` only show the value, not `key=value` (#313 by [@bbc2]).

### Added

- Add `--override`/`--no-override` option to `dotenv run` (#312 by [@zueve] and [@bbc2]).

## [0.16.0] - 2021-03-27

### Changed

- The default value of the `encoding` parameter for `load_dotenv` and `dotenv_values` is
  now `"utf-8"` instead of `None` (#306 by [@bbc2]).
- Fix resolution order in variable expansion with `override=False` (#287 by [@bbc2]).

## [0.15.0] - 2020-10-28

### Added

- Add `--export` option to `set` to make it prepend the binding with `export` (#270 by
  [@jadutter]).

### Changed

- Make `set` command create the `.env` file in the current directory if no `.env` file was
  found (#270 by [@jadutter]).

### Fixed

- Fix potentially empty expanded value for duplicate key (#260 by [@bbc2]).
- Fix import error on Python 3.5.0 and 3.5.1 (#267 by [@gongqingkui]).
- Fix parsing of unquoted values containing several adjacent space or tab characters
  (#277 by [@bbc2], review by [@x-yuri]).

## [0.14.0] - 2020-07-03

### Changed

- Privilege definition in file over the environment in variable expansion (#256 by
  [@elbehery95]).

### Fixed

- Improve error message for when file isn't found (#245 by [@snobu]).
- Use HTTPS URL in package meta data (#251 by [@ekohl]).

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

- Add tests for docs ([@Flimm])
- Make 'cli' support optional. Use `pip install python-dotenv[cli]`. ([@theskumar])

## 0.8.0

- `set_key` and `unset_key` only modified the affected file instead of
  parsing and re-writing file, this causes comments and other file
  entact as it is.
- Add support for `export` prefix in the line.
- Internal refractoring ([@theskumar])
- Allow `load_dotenv` and `dotenv_values` to work with `StringIO())` ([@alanjds])([@theskumar])([#78])

## 0.7.1

- Remove hard dependency on iPython ([@theskumar])

## 0.7.0

- Add support to override system environment variable via .env.
  ([@milonimrod](https://github.com/milonimrod))
  ([\#63](https://github.com/theskumar/python-dotenv/issues/63))
- Disable ".env not found" warning by default
  ([@maxkoryukov](https://github.com/maxkoryukov))
  ([\#57](https://github.com/theskumar/python-dotenv/issues/57))

## 0.6.5

- Add support for special characters `\`.
  ([@pjona](https://github.com/pjona))
  ([\#60](https://github.com/theskumar/python-dotenv/issues/60))

## 0.6.4

- Fix issue with single quotes ([@Flimm])
  ([\#52](https://github.com/theskumar/python-dotenv/issues/52))

## 0.6.3

- Handle unicode exception in setup.py
  ([\#46](https://github.com/theskumar/python-dotenv/issues/46))

## 0.6.2

- Fix dotenv list command ([@ticosax](https://github.com/ticosax))
- Add iPython Support
  ([@tillahoffmann](https://github.com/tillahoffmann))

## 0.6.0

- Drop support for Python 2.6
- Handle escaped characters and newlines in quoted values. (Thanks
  [@iameugenejo](https://github.com/iameugenejo))
- Remove any spaces around unquoted key/value. (Thanks
  [@paulochf](https://github.com/paulochf))
- Added POSIX variable expansion. (Thanks
  [@hugochinchilla](https://github.com/hugochinchilla))

## 0.5.1

- Fix `find_dotenv` - it now start search from the file where this
  function is called from.

## 0.5.0

- Add `find_dotenv` method that will try to find a `.env` file.
  (Thanks [@isms](https://github.com/isms))

## 0.4.0

- cli: Added `-q/--quote` option to control the behaviour of quotes
  around values in `.env`. (Thanks
  [@hugochinchilla](https://github.com/hugochinchilla)).
- Improved test coverage.

<!-- PR LINKS -->

[#78]: https://github.com/theskumar/python-dotenv/issues/78
[#121]: https://github.com/theskumar/python-dotenv/issues/121
[#148]: https://github.com/theskumar/python-dotenv/issues/148
[#158]: https://github.com/theskumar/python-dotenv/issues/158
[#170]: https://github.com/theskumar/python-dotenv/issues/170
[#172]: https://github.com/theskumar/python-dotenv/issues/172
[#176]: https://github.com/theskumar/python-dotenv/issues/176
[#183]: https://github.com/theskumar/python-dotenv/issues/183
[#359]: https://github.com/theskumar/python-dotenv/issues/359
[#469]: https://github.com/theskumar/python-dotenv/issues/469
[#456]: https://github.com/theskumar/python-dotenv/issues/456
[#466]: https://github.com/theskumar/python-dotenv/issues/466
[#454]: https://github.com/theskumar/python-dotenv/issues/454
[#474]: https://github.com/theskumar/python-dotenv/issues/474
[#523]: https://github.com/theskumar/python-dotenv/issues/523
[#553]: https://github.com/theskumar/python-dotenv/issues/553
[#569]: https://github.com/theskumar/python-dotenv/issues/569
[#583]: https://github.com/theskumar/python-dotenv/issues/583
[#586]: https://github.com/theskumar/python-dotenv/issues/586
[#590]: https://github.com/theskumar/python-dotenv/issues/590
[#607]: https://github.com/theskumar/python-dotenv/issues/607
[#588]: https://github.com/theskumar/python-dotenv/issues/588
[#579]: https://github.com/theskumar/python-dotenv/pull/579
[#566]: https://github.com/theskumar/python-dotenv/pull/566
[#563]: https://github.com/theskumar/python-dotenv/pull/563
[#497]: https://github.com/theskumar/python-dotenv/pull/497
[#161]: https://github.com/theskumar/python-dotenv/issues/161
[790c5c0]: https://github.com/theskumar/python-dotenv/commit/790c5c02991100aa1bf41ee5330aca75edc51311

<!-- contributors -->

[@23f3001135]: https://github.com/23f3001135
[@EpicWink]: https://github.com/EpicWink
[@Flimm]: https://github.com/Flimm
[@Nicals]: https://github.com/Nicals
[@Nougat-Waffle]: https://github.com/Nougat-Waffle
[@Qwerty-133]: https://github.com/Qwerty-133
[@alanjds]: https://github.com/alanjds
[@altendky]: https://github.com/altendky
[@andrewsmith]: https://github.com/andrewsmith
[@asyncee]: https://github.com/asyncee
[@bbc2]: https://github.com/bbc2
[@befeleme]: https://github.com/befeleme
[@cjauvin]: https://github.com/cjauvin
[@eaf]: https://github.com/eaf
[@earlbread]: https://github.com/earlbread
[@eekstunt]: https://github.com/eekstunt
[@eggplants]: https://github.com/eggplants
[@ekohl]: https://github.com/ekohl
[@elbehery95]: https://github.com/elbehery95
[@eumiro]: https://github.com/eumiro
[@freddyaboulton]: https://github.com/freddyaboulton
[@gergelyk]: https://github.com/gergelyk
[@gongqingkui]: https://github.com/gongqingkui
[@greyli]: https://github.com/greyli
[@harveer07]: https://github.com/harveer07
[@jadutter]: https://github.com/jadutter
[@jankislinger]: https://github.com/jankislinger
[@jctanner]: https://github.com/jctanner
[@larsks]: https://github.com/larsks
[@lsmith77]: https://github.com/lsmith77
[@matthewfranglen]: https://github.com/matthewfranglen
[@mgorny]: https://github.com/mgorny
[@naorlivne]: https://github.com/naorlivne
[@qnighy]: https://github.com/qnighy
[@rabinadk1]: https://github.com/rabinadk1
[@randomseed42]: https://github.com/randomseed42
[@sammck]: https://github.com/sammck
[@samwyma]: https://github.com/samwyma
[@sidharth-sudhir]: https://github.com/sidharth-sudhir
[@snobu]: https://github.com/snobu
[@techalchemy]: https://github.com/techalchemy
[@theGOTOguy]: https://github.com/theGOTOguy
[@theskumar]: https://github.com/theskumar
[@ulyssessouza]: https://github.com/ulyssessouza
[@venthur]: https://github.com/venthur
[@wrongontheinternet]: https://github.com/wrongontheinternet
[@x-yuri]: https://github.com/x-yuri
[@yannham]: https://github.com/yannham
[@zueve]: https://github.com/zueve
[@JYOuyang]: https://github.com/JYOuyang
[@burnout-projects]: https://github.com/burnout-projects
[@cpackham-atlnz]: https://github.com/cpackham-atlnz
[Unreleased]: https://github.com/theskumar/python-dotenv/compare/v1.2.2...HEAD
[1.2.2]: https://github.com/theskumar/python-dotenv/compare/v1.2.1...v1.2.2
[1.2.1]: https://github.com/theskumar/python-dotenv/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/theskumar/python-dotenv/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/theskumar/python-dotenv/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/theskumar/python-dotenv/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/theskumar/python-dotenv/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/theskumar/python-dotenv/compare/v0.21.0...v1.0.0
[0.21.1]: https://github.com/theskumar/python-dotenv/compare/v0.21.0...v0.21.1
[0.21.0]: https://github.com/theskumar/python-dotenv/compare/v0.20.0...v0.21.0
[0.20.0]: https://github.com/theskumar/python-dotenv/compare/v0.19.2...v0.20.0
[0.19.2]: https://github.com/theskumar/python-dotenv/compare/v0.19.1...v0.19.2
[0.19.1]: https://github.com/theskumar/python-dotenv/compare/v0.19.0...v0.19.1
[0.19.0]: https://github.com/theskumar/python-dotenv/compare/v0.18.0...v0.19.0
[0.18.0]: https://github.com/theskumar/python-dotenv/compare/v0.17.1...v0.18.0
[0.17.1]: https://github.com/theskumar/python-dotenv/compare/v0.17.0...v0.17.1
[0.17.0]: https://github.com/theskumar/python-dotenv/compare/v0.16.0...v0.17.0
[0.16.0]: https://github.com/theskumar/python-dotenv/compare/v0.15.0...v0.16.0
[0.15.0]: https://github.com/theskumar/python-dotenv/compare/v0.14.0...v0.15.0
[0.14.0]: https://github.com/theskumar/python-dotenv/compare/v0.13.0...v0.14.0
[0.13.0]: https://github.com/theskumar/python-dotenv/compare/v0.12.0...v0.13.0
[0.12.0]: https://github.com/theskumar/python-dotenv/compare/v0.11.0...v0.12.0
[0.11.0]: https://github.com/theskumar/python-dotenv/compare/v0.10.5...v0.11.0
[0.10.5]: https://github.com/theskumar/python-dotenv/compare/v0.10.4...v0.10.5
[0.10.4]: https://github.com/theskumar/python-dotenv/compare/v0.10.3...v0.10.4
