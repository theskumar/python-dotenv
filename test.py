"""Temporary manual test (for Windows)"""
# pip install -e .
# python test.py

import dotenv
import io
import os

os.environ["TEST"] = "ttt"
os.environ["EMPTY"] = ""
# os.environ["NOT_DEFINED"]=""


def test(str):
    print(str, dotenv.dotenv_values(stream=io.StringIO(str)))


test("FOO=bar")
test("FOO=$bar")        # :(, but ok, more strict with {}
test("FOO=${bar}")
test("FOO=\"$bar\"")
test("FOO=\"${bar}\"")
test("FOO='$bar'")
test("FOO='${bar}'")    # little confusing
test("FOO='\\$\\{bar\\}'")    # but we have this
test("FOO=\$\{bar\}")         # but we have this, but...

test("FOO_ok=${NOT_DEFINED-ok}")
test("FOO_ok=${NOT_DEFINED:-ok}")
test("FOO_em=${EMPTY-ok}")
test("FOO_ok=${EMPTY:-ok}")
test("FOO_ttt=${TEST-ok}")
test("FOO_ttt=${TEST:-ok}")

test("FOO_ok=${TEST+ok}")
test("FOO_ok=${TEST:+ok}")
test("FOO_ok=${EMPTY+ok}")
test("FOO_em=${EMPTY:+ok}")
test("FOO_em=${NOT_DEFINED:+ok}")
test("FOO_em=${NOT_DEFINED:+ok}")

test("FOO_em=${TEST?no throw}")
test("FOO_em=${TEST:?no throw}")
test("FOO_em=${EMPTY?no throw}")

try:
    test("FOO_em=${EMPTY:?throw}")
except LookupError as ex:
    print(f"ex is {ex}")

try:
    test("FOO_em=${NOT_DEFINED:?throw}")
except LookupError as ex:
    print(f"ex is {ex}")

try:
    test("FOO_em=${NOT_DEFINED?throw}")
except LookupError as ex:
    print(f"ex is {ex}")
