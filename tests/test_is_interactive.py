import sys
import builtins
from unittest import mock
from dotenv.main import find_dotenv


class TestIsInteractive:
    """Tests for the _is_interactive helper function within find_dotenv.

    The _is_interactive function is used by find_dotenv to determine if the code
    is running in an interactive environment (like a REPL, IPython notebook, etc.)
    versus a normal script execution.

    Interactive environments include:
    - Python REPL (has sys.ps1 or sys.ps2)
    - IPython notebooks (no __file__ in __main__)
    - Interactive shells

    Non-interactive environments include:
    - Normal script execution (has __file__ in __main__)
    - Module imports

    Examples of the behavior:
    >>> import sys
    >>> # In a REPL:
    >>> hasattr(sys, 'ps1')  # True
    >>> # In a script:
    >>> hasattr(sys, 'ps1')  # False
    """

    def _create_dotenv_file(self, tmp_path):
        """Helper to create a test .env file."""
        dotenv_path = tmp_path / ".env"
        dotenv_path.write_text("TEST=value")
        return dotenv_path

    def _setup_subdir_and_chdir(self, tmp_path, monkeypatch):
        """Helper to create subdirectory and change to it."""
        test_dir = tmp_path / "subdir"
        test_dir.mkdir()
        monkeypatch.chdir(test_dir)
        return test_dir

    def _remove_ps_attributes(self, monkeypatch):
        """Helper to remove ps1/ps2 attributes if they exist."""
        if hasattr(sys, "ps1"):
            monkeypatch.delattr(sys, "ps1")
        if hasattr(sys, "ps2"):
            monkeypatch.delattr(sys, "ps2")

    def _mock_main_import(self, monkeypatch, mock_main_module):
        """Helper to mock __main__ module import."""
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "__main__":
                return mock_main_module
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

    def _mock_main_import_error(self, monkeypatch):
        """Helper to mock __main__ module import that raises ModuleNotFoundError."""
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "__main__":
                raise ModuleNotFoundError("No module named '__main__'")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

    def test_is_interactive_with_ps1(self, tmp_path, monkeypatch):
        """Test that _is_interactive returns True when sys.ps1 exists."""
        dotenv_path = self._create_dotenv_file(tmp_path)

        # Mock sys.ps1 to simulate interactive shell
        monkeypatch.setattr(sys, "ps1", ">>> ", raising=False)

        self._setup_subdir_and_chdir(tmp_path, monkeypatch)

        # When _is_interactive() returns True, find_dotenv should search from cwd
        result = find_dotenv()
        assert result == str(dotenv_path)

    def test_is_interactive_with_ps2(self, tmp_path, monkeypatch):
        """Test that _is_interactive returns True when sys.ps2 exists."""
        dotenv_path = self._create_dotenv_file(tmp_path)

        # Mock sys.ps2 to simulate multi-line interactive input
        monkeypatch.setattr(sys, "ps2", "... ", raising=False)

        self._setup_subdir_and_chdir(tmp_path, monkeypatch)

        # When _is_interactive() returns True, find_dotenv should search from cwd
        result = find_dotenv()
        assert result == str(dotenv_path)

    def test_is_interactive_main_module_not_found(self, tmp_path, monkeypatch):
        """Test that _is_interactive returns False when __main__ module import fails."""
        self._remove_ps_attributes(monkeypatch)
        self._mock_main_import_error(monkeypatch)

        # Change to directory and test
        monkeypatch.chdir(tmp_path)

        # Since _is_interactive() returns False, find_dotenv should not find anything
        # without usecwd=True
        result = find_dotenv()
        assert result == ""

    def test_is_interactive_main_without_file(self, tmp_path, monkeypatch):
        """Test that _is_interactive returns True when __main__ has no __file__ attribute."""
        self._remove_ps_attributes(monkeypatch)
        dotenv_path = self._create_dotenv_file(tmp_path)

        # Mock __main__ module without __file__ attribute
        mock_main = mock.MagicMock()
        del mock_main.__file__  # Remove __file__ attribute

        self._mock_main_import(monkeypatch, mock_main)
        self._setup_subdir_and_chdir(tmp_path, monkeypatch)

        # When _is_interactive() returns True, find_dotenv should search from cwd
        result = find_dotenv()
        assert result == str(dotenv_path)

    def test_is_interactive_main_with_file(self, tmp_path, monkeypatch):
        """Test that _is_interactive returns False when __main__ has __file__ attribute."""
        self._remove_ps_attributes(monkeypatch)

        # Mock __main__ module with __file__ attribute
        mock_main = mock.MagicMock()
        mock_main.__file__ = "/path/to/script.py"

        self._mock_main_import(monkeypatch, mock_main)

        # Change to directory and test
        monkeypatch.chdir(tmp_path)

        # Since _is_interactive() returns False, find_dotenv should not find anything
        # without usecwd=True
        result = find_dotenv()
        assert result == ""

    def test_is_interactive_precedence_ps1_over_main(self, tmp_path, monkeypatch):
        """Test that ps1/ps2 attributes take precedence over __main__ module check."""
        dotenv_path = self._create_dotenv_file(tmp_path)

        # Set ps1 attribute
        monkeypatch.setattr(sys, "ps1", ">>> ", raising=False)

        # Mock __main__ module with __file__ attribute (which would normally return False)
        mock_main = mock.MagicMock()
        mock_main.__file__ = "/path/to/script.py"

        self._mock_main_import(monkeypatch, mock_main)
        self._setup_subdir_and_chdir(tmp_path, monkeypatch)

        # ps1 should take precedence, so _is_interactive() returns True
        result = find_dotenv()
        assert result == str(dotenv_path)

    def test_is_interactive_ps1_and_ps2_both_exist(self, tmp_path, monkeypatch):
        """Test that _is_interactive returns True when both ps1 and ps2 exist."""
        dotenv_path = self._create_dotenv_file(tmp_path)

        # Set both ps1 and ps2 attributes
        monkeypatch.setattr(sys, "ps1", ">>> ", raising=False)
        monkeypatch.setattr(sys, "ps2", "... ", raising=False)

        self._setup_subdir_and_chdir(tmp_path, monkeypatch)

        # Should return True with either attribute present
        result = find_dotenv()
        assert result == str(dotenv_path)

    def test_is_interactive_main_module_with_file_attribute_none(self, tmp_path, monkeypatch):
        """Test _is_interactive when __main__ has __file__ attribute set to None."""
        self._remove_ps_attributes(monkeypatch)

        # Mock __main__ module with __file__ = None
        mock_main = mock.MagicMock()
        mock_main.__file__ = None

        self._mock_main_import(monkeypatch, mock_main)

        # Mock sys.gettrace to ensure debugger detection returns False
        monkeypatch.setattr("sys.gettrace", lambda: None)

        monkeypatch.chdir(tmp_path)

        # __file__ = None should still be considered non-interactive
        # and with no debugger, find_dotenv should not search from cwd
        result = find_dotenv()
        assert result == ""

    def test_is_interactive_no_ps_attributes_and_normal_execution(self, tmp_path, monkeypatch):
        """Test normal script execution scenario where _is_interactive should return False."""
        self._remove_ps_attributes(monkeypatch)

        # Don't mock anything - let it use the real __main__ module
        # which should have a __file__ attribute in normal execution

        # Change to directory and test
        monkeypatch.chdir(tmp_path)

        # In normal execution, _is_interactive() should return False
        # so find_dotenv should not find anything without usecwd=True
        result = find_dotenv()
        assert result == ""

    def test_is_interactive_with_usecwd_override(self, tmp_path, monkeypatch):
        """Test that usecwd=True overrides _is_interactive behavior."""
        self._remove_ps_attributes(monkeypatch)
        dotenv_path = self._create_dotenv_file(tmp_path)

        # Mock __main__ module with __file__ attribute (non-interactive)
        mock_main = mock.MagicMock()
        mock_main.__file__ = "/path/to/script.py"

        self._mock_main_import(monkeypatch, mock_main)
        self._setup_subdir_and_chdir(tmp_path, monkeypatch)

        # Even though _is_interactive() returns False, usecwd=True should find the file
        result = find_dotenv(usecwd=True)
        assert result == str(dotenv_path)
