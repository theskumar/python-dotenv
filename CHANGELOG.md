# Install the latest

To install the latest version of `python-dotenv` simply run:

`pip install python-dotenv`

OR

`poetry add python-dotenv`

OR

`pipenv install python-dotenv`


Changelog
=========

0.10.5
-----

- Fix handling of malformed lines and lines without a value ([@bbc2])([#222]):
  - Don't print warning when key has no value.
  - Reject more malformed lines (e.g. "A: B").
- Fix handling of lines with just a comment ([@bbc2])([#224]).

0.10.4
-----

- Make typing optional ([@techalchemy])([#179]).
- Print a warning on malformed line ([@bbc2])([#211]).
- Support keys without a value ([@ulyssessouza])([#220]).

0.10.3
-----

- Improve interactive mode detection ([@andrewsmith])([#183]).
- Refactor parser to fix parsing inconsistencies ([@bbc2])([#170]).
  - Interpret escapes as control characters only in double-quoted strings.
  - Interpret `#` as start of comment only if preceded by whitespace.

0.10.2
-----

- Add type hints and expose them to users ([@qnighy])([#172])
- `load_dotenv` and `dotenv_values` now accept an `encoding` parameter, defaults to `None`
  ([@theskumar])([@earlbread])([#161])
- Fix `str`/`unicode` inconsistency in Python 2: values are always `str` now. ([@bbc2])([#121])
- Fix Unicode error in Python 2, introduced in 0.10.0. ([@bbc2])([#176])

0.10.1
-----
- Fix parsing of variable without a value ([@asyncee])([@bbc2])([#158])

0.10.0
-----

- Add support for UTF-8 in unquoted values ([@bbc2])([#148])
- Add support for trailing comments ([@bbc2])([#148])
- Add backslashes support in values ([@bbc2])([#148])
- Add support for newlines in values ([@bbc2])([#148])
- Force environment variables to str with Python2 on Windows ([@greyli])
- Drop Python 3.3 support ([@greyli])
- Fix stderr/-out/-in redirection ([@venthur])


0.9.0
-----
- Add `--version` parameter to cli ([@venthur])
- Enable loading from current directory ([@cjauvin])
- Add 'dotenv run' command for calling arbitrary shell script with .env ([@venthur])

0.8.1
-----

-   Add tests for docs ([@Flimm])
-   Make 'cli' support optional. Use `pip install python-dotenv[cli]`. ([@theskumar])

0.8.0
-----

-   `set_key` and `unset_key` only modified the affected file instead of
    parsing and re-writing file, this causes comments and other file
    entact as it is.
-   Add support for `export` prefix in the line.
-   Internal refractoring ([@theskumar])
-   Allow `load_dotenv` and `dotenv_values` to work with `StringIO())` ([@alanjds])([@theskumar])([#78])

0.7.1
-----

-   Remove hard dependency on iPython ([@theskumar])

0.7.0
-----

-   Add support to override system environment variable via .env.
    ([@milonimrod](https://github.com/milonimrod))
    ([\#63](https://github.com/theskumar/python-dotenv/issues/63))
-   Disable ".env not found" warning by default
    ([@maxkoryukov](https://github.com/maxkoryukov))
    ([\#57](https://github.com/theskumar/python-dotenv/issues/57))

0.6.5
-----

-   Add support for special characters `\`.
    ([@pjona](https://github.com/pjona))
    ([\#60](https://github.com/theskumar/python-dotenv/issues/60))

0.6.4
-----

-   Fix issue with single quotes ([@Flimm])
    ([\#52](https://github.com/theskumar/python-dotenv/issues/52))

0.6.3
-----

-   Handle unicode exception in setup.py
    ([\#46](https://github.com/theskumar/python-dotenv/issues/46))

0.6.2
-----

-   Fix dotenv list command ([@ticosax](https://github.com/ticosax))
-   Add iPython Suport
    ([@tillahoffmann](https://github.com/tillahoffmann))

0.6.0
-----

-   Drop support for Python 2.6
-   Handle escaped charaters and newlines in quoted values. (Thanks
    [@iameugenejo](https://github.com/iameugenejo))
-   Remove any spaces around unquoted key/value. (Thanks
    [@paulochf](https://github.com/paulochf))
-   Added POSIX variable expansion. (Thanks
    [@hugochinchilla](https://github.com/hugochinchilla))

0.5.1
-----

-   Fix find\_dotenv - it now start search from the file where this
    function is called from.

0.5.0
-----

-   Add `find_dotenv` method that will try to find a `.env` file.
    (Thanks [@isms](https://github.com/isms))

0.4.0
-----

-   cli: Added `-q/--quote` option to control the behaviour of quotes
    around values in `.env`. (Thanks
    [@hugochinchilla](https://github.com/hugochinchilla)).
-   Improved test coverage.

[#161]: https://github.com/theskumar/python-dotenv/issues/161
[#78]: https://github.com/theskumar/python-dotenv/issues/78
[#148]: https://github.com/theskumar/python-dotenv/issues/148
[#158]: https://github.com/theskumar/python-dotenv/issues/158
[#172]: https://github.com/theskumar/python-dotenv/issues/172
[#121]: https://github.com/theskumar/python-dotenv/issues/121
[#176]: https://github.com/theskumar/python-dotenv/issues/176
[#170]: https://github.com/theskumar/python-dotenv/issues/170
[#183]: https://github.com/theskumar/python-dotenv/issues/183

[@andrewsmith]: https://github.com/andrewsmith
[@asyncee]: https://github.com/asyncee
[@greyli]: https://github.com/greyli
[@venthur]: https://github.com/venthur
[@Flimm]: https://github.com/Flimm
[@theskumar]: https://github.com/theskumar
[@alanjds]: https://github.com/alanjds
[@cjauvin]: https://github.com/cjauvin
[@bbc2]: https://github.com/bbc2
[@qnighy]: https://github.com/qnighy
[@earlbread]: https://github.com/earlbread
