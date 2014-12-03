import os
import re
import sys
import warnings


line_re = re.compile(r"""
    ^
    (?:export\s+)?      # optional export
    ([\w\.]+)           # key
    (?:\s*=\s*|:\s+?)   # separator
    (                   # optional value begin
        '(?:\'|[^'])*'  #   single quoted value
        |               #   or
        "(?:\"|[^"])*"  #   double quoted value
        |               #   or
        [^#\n]+         #   unquoted value
    )?                  # value end
    (?:\s*\#.*)?        # optional comment
    $
""", re.VERBOSE)

variable_re = re.compile(r"""
    (\\)?               # is it escaped with a backslash?
    (\$)                # literal $
    (                   # collect braces with var for sub
        \{?             #   allow brace wrapping
        ([A-Z0-9_]+)    #   match the variable
        \}?             #   closing brace
    )                   # braces end
""", re.IGNORECASE | re.VERBOSE)


def read_dotenv(dotenv=None):
    """
    Read a .env file into os.environ.

    If not given a path to a dotenv path, does filthy magic stack backtracking
    to find manage.py and then find the dotenv.
    """
    if dotenv is None:
        frame = sys._getframe()
        dotenv = os.path.join(os.path.dirname(frame.f_back.f_code.co_filename), '.env')
    if os.path.exists(dotenv):
        file = open(dotenv)
        for k, v in parse_dotenv(file.read()).items():
            os.environ.setdefault(k, v)
        file.close()
    else:
        warnings.warn("not reading %s - it doesn't exist." % dotenv)


def parse_dotenv(content):
    env = {}
    for line in content.splitlines():
        m1 = line_re.search(line)
        if m1:
            key, value = m1.groups()
            if value is None:
                value = ''

            # remove leading/trailing whitespace
            value = value.strip()

            # remove surrounding quotes
            m2 = re.match(r'^([\'"])(.*)\1$', value)
            if m2:
                quotemark, value = m2.groups()
            else:
                quotemark = None

            # unescape all characters except $ so variables can be escaped properly
            if quotemark == '"':
                value = re.sub(r'\\([^$])', '\1', value)

            if quotemark != "'":
                # substitute variables in a value
                for parts in variable_re.findall(value):
                    if parts[0] == '\\':
                        # variable is escaped, don't replace it
                        replace = ''.join(parts[1:-1])
                    else:
                        # replace it with the value from the environment
                        replace = env.get(parts[-1], os.environ.get(parts[-1], ''))
                    value = value.replace(''.join(parts[0:-1]), replace)

            env[key] = value
        elif not re.search(r'^\s*(?:#.*)?$', line):  # not comment or blank line
            warnings.warn("Line %s doesn't match format" % repr(line), SyntaxWarning)
    return env
