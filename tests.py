import os
import shutil
import unittest
import warnings

from dotenv import parse_dotenv, read_dotenv


class ParseDotenvTestCase(unittest.TestCase):
    def test_parses_unquoted_values(self):
        env = parse_dotenv('FOO=bar')
        self.assertEqual(env, {'FOO': 'bar'})

    def test_parses_values_with_spaces_around_equal_sign(self):
        env = parse_dotenv('FOO =bar')
        self.assertEqual(env, {'FOO': 'bar'})

        env = parse_dotenv('FOO= bar')
        self.assertEqual(env, {'FOO': 'bar'})

    def test_parses_double_quoted_values(self):
        env = parse_dotenv('FOO="bar"')
        self.assertEqual(env, {'FOO': 'bar'})

    def test_parses_single_quoted_values(self):
        env = parse_dotenv("FOO='bar'")
        self.assertEqual(env, {'FOO': 'bar'})

    def test_parses_escaped_double_quotes(self):
        env = parse_dotenv('FOO="escaped\\"bar"')
        self.assertEqual(env, {'FOO': 'escaped"bar'})

    def test_parses_empty_values(self):
        env = parse_dotenv('FOO=')
        self.assertEqual(env, {'FOO': ''})

    def test_expands_variables_found_in_values(self):
        env = parse_dotenv("FOO=test\nBAR=$FOO")
        self.assertEqual(env, {'FOO': 'test', 'BAR': 'test'})

    def test_expands_variables_wrapped_in_brackets(self):
        env = parse_dotenv("FOO=test\nBAR=${FOO}bar")
        self.assertEqual(env, {'FOO': 'test', 'BAR': 'testbar'})

    def test_expands_variables_from_environ_if_not_found_in_local_env(self):
        os.environ.setdefault('FOO', 'test')
        env = parse_dotenv('BAR=$FOO')
        self.assertEqual(env, {'BAR': 'test'})

    def test_expands_undefined_variables_to_an_empty_string(self):
        self.assertEqual(parse_dotenv('BAR=$FOO'), {'BAR': ''})

    def test_expands_variables_in_double_quoted_values(self):
        env = parse_dotenv("FOO=test\nBAR=\"quote $FOO\"")
        self.assertEqual(env, {'FOO': 'test', 'BAR': 'quote test'})

    def test_does_not_expand_variables_in_single_quoted_values(self):
        env = parse_dotenv("BAR='quote $FOO'")
        self.assertEqual(env, {'BAR': 'quote $FOO'})

    def test_does_not_expand_escaped_variables(self):
        env = parse_dotenv('FOO="foo\\$BAR"')
        self.assertEqual(env, {'FOO': 'foo$BAR'})

        env = parse_dotenv('FOO="foo\${BAR}"')
        self.assertEqual(env, {'FOO': 'foo${BAR}'})

    def test_parses_export_keyword(self):
        env = parse_dotenv('export FOO=bar')
        self.assertEqual(env, {'FOO': 'bar'})

    def test_parses_key_with_dot_in_the_name(self):
        env = parse_dotenv('FOO.BAR=foobar')
        self.assertEqual(env, {'FOO.BAR': 'foobar'})

    def test_strips_unquoted_values(self):
        env = parse_dotenv('foo=bar ')
        self.assertEqual(env, {'foo': 'bar'})  # not 'bar '

    def test_warns_if_line_format_is_incorrect(self):
        with warnings.catch_warnings(record=True) as w:
            parse_dotenv('lol$wut')

            self.assertEqual(len(w), 1)
            self.assertTrue(w[0].category is SyntaxWarning)
            self.assertEqual(
                str(w[0].message),
                "Line 'lol$wut' doesn't match format"
            )

    def test_ignores_empty_lines(self):
        env = parse_dotenv("\n \t  \nfoo=bar\n \nfizz=buzz")
        self.assertEqual(env, {'foo': 'bar', 'fizz': 'buzz'})

    def test_ignores_inline_comments(self):
        env = parse_dotenv('foo=bar # this is foo')
        self.assertEqual(env, {'foo': 'bar'})

    def test_allows_hash_in_quoted_values(self):
        env = parse_dotenv('foo="bar#baz" # comment ')
        self.assertEqual(env, {'foo': 'bar#baz'})

    def test_ignores_comment_lines(self):
        env = parse_dotenv("\n\n\n # HERE GOES FOO \nfoo=bar")
        self.assertEqual(env, {'foo': 'bar'})

    def test_parses_hash_in_quoted_values(self):
        env = parse_dotenv('foo="ba#r"')
        self.assertEqual(env, {'foo': 'ba#r'})

        env = parse_dotenv('foo="ba#r"')
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
            self.assertTrue(w[0].category is UserWarning)
            self.assertEqual(
                str(w[0].message),
                "Not reading .does_not_exist - it doesn't exist."
            )


class ParseDotenvDirectoryTestCase(unittest.TestCase):
    """Test parsing a dotenv file given the directory where it lives"""

    def setUp(self):
        # Define our dotenv directory
        self.dotenv_dir = os.path.join(
            os.path.dirname(__file__), 'dotenv_dir')
        # Create the directory
        os.mkdir(self.dotenv_dir)
        # Copy the test .env file to our new directory
        shutil.copy2(os.path.abspath('.env'), self.dotenv_dir)

    def tearDown(self):
        if os.path.exists(self.dotenv_dir):
            shutil.rmtree(self.dotenv_dir)

    def test_can_read_dotenv_given_its_directory(self):
        read_dotenv(self.dotenv_dir)
        self.assertEqual(os.environ.get('DOTENV'), 'true')
