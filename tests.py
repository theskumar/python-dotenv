import os
import unittest
import warnings

from dotenv import parse_dotenv, read_dotenv


class ParseDotenvTestCase(unittest.TestCase):
    def test_parses_unquoted_values(self):
        self.assertEqual(parse_dotenv('FOO=bar'), {'FOO': 'bar'})

    def test_parses_values_with_spaces_around_equal_sign(self):
        self.assertEqual(parse_dotenv('FOO =bar'), {'FOO': 'bar'})
        self.assertEqual(parse_dotenv('FOO= bar'), {'FOO': 'bar'})

    def test_parses_double_quoted_values(self):
        self.assertEqual(parse_dotenv('FOO="bar"'), {'FOO': 'bar'})

    def test_parses_single_quoted_values(self):
        self.assertEqual(parse_dotenv("FOO='bar'"), {'FOO': 'bar'})

    def test_parses_escaped_double_quotes(self):
        self.assertEqual(parse_dotenv('FOO="escaped\"bar"'), {'FOO': 'escaped"bar'})

    def test_parses_empty_values(self):
        self.assertEqual(parse_dotenv('FOO='), {'FOO': ''})

    def test_expands_variables_found_in_values(self):
        self.assertEqual(parse_dotenv("FOO=test\nBAR=$FOO"), {'FOO': 'test', 'BAR': 'test'})

    def test_expands_variables_wrapped_in_brackets(self):
        self.assertEqual(parse_dotenv("FOO=test\nBAR=${FOO}bar"), {'FOO': 'test', 'BAR': 'testbar'})

    def test_expands_variables_from_environ_if_not_found_in_local_env(self):
        os.environ.setdefault('FOO', 'test')
        self.assertEqual(parse_dotenv('BAR=$FOO'), {'BAR': 'test'})

    def test_expands_undefined_variables_to_an_empty_string(self):
        self.assertEqual(parse_dotenv('BAR=$FOO'), {'BAR': ''})

    def test_expands_variables_in_double_quoted_values(self):
        self.assertEqual(parse_dotenv("FOO=test\nBAR=\"quote $FOO\""), {'FOO': 'test', 'BAR': 'quote test'})

    def test_does_not_expand_variables_in_single_quoted_values(self):
        self.assertEqual(parse_dotenv("BAR='quote $FOO'"), {'BAR': 'quote $FOO'})

    def test_does_not_expand_escaped_variables(self):
        self.assertEqual(parse_dotenv('FOO="foo\\$BAR"'), {'FOO': 'foo$BAR'})
        self.assertEqual(parse_dotenv('FOO="foo\${BAR}"'), {'FOO': 'foo${BAR}'})

    def test_parses_export_keyword(self):
        self.assertEqual(parse_dotenv('export FOO=bar'), {'FOO': 'bar'})

    def test_parses_key_with_dot_in_the_name(self):
        self.assertEqual(parse_dotenv('FOO.BAR=foobar'), {'FOO.BAR': 'foobar'})

    def test_strips_unquoted_values(self):
        self.assertEqual(parse_dotenv('foo=bar '), {'foo': 'bar'})  # not 'bar '

    def test_warns_if_line_format_is_incorrect(self):
        with warnings.catch_warnings(record=True) as w:
            parse_dotenv('lol$wut')

            self.assertEqual(len(w), 1)
            self.assertIs(w[0].category, SyntaxWarning)
            self.assertEqual(str(w[0].message), "Line 'lol$wut' doesn't match format")

    def test_ignores_empty_lines(self):
        self.assertEqual(parse_dotenv("\n \t  \nfoo=bar\n \nfizz=buzz"), {'foo': 'bar', 'fizz': 'buzz'})

    def test_ignores_inline_comments(self):
        self.assertEqual(parse_dotenv('foo=bar # this is foo'), {'foo': 'bar'})

    def test_allows_hash_in_quoted_values(self):
        self.assertEqual(parse_dotenv('foo="bar#baz" # comment '), {'foo': 'bar#baz'})

    def test_ignores_comment_lines(self):
        self.assertEqual(parse_dotenv("\n\n\n # HERE GOES FOO \nfoo=bar"), {'foo': 'bar'})

    def test_parses_hash_in_quoted_values(self):
        self.assertEqual(parse_dotenv('foo="ba#r"'), {'foo': 'ba#r'})
        self.assertEqual(parse_dotenv("foo='ba#r'"), {'foo': 'ba#r'})


class ReadDotenvTestCase(unittest.TestCase):
    def test_defaults_to_dotenv(self):
        read_dotenv()
        self.assertEqual(os.environ.get('DOTENV'), 'true')

    def test_reads_the_file(self):
        read_dotenv('.env')
        self.assertEqual(os.environ.get('DOTENV'), 'true')

    def test_warns_if_file_does_not_exist(self):
        with warnings.catch_warnings(record=True) as w:
            read_dotenv('.does_not_exist')

            self.assertEqual(len(w), 1)
            self.assertIs(w[0].category, UserWarning)
            self.assertEqual(str(w[0].message), "not reading .does_not_exist - it doesn't exist.")
