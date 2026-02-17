import json
import os
import pytest
from mcp_backpack import server

_real_get_project_paths = server.get_project_paths


@pytest.fixture(autouse=True)
def tmp_project(tmp_path, monkeypatch):
    """Redirect all backpack operations to a temp directory."""
    memory_dir = os.path.join(str(tmp_path), ".backpack_memory")
    monkeypatch.setattr(server, "get_project_paths", lambda: (str(tmp_path), memory_dir))
    return tmp_path


class TestPutAndCheck:
    def test_basic_store_and_retrieve(self):
        put_in_backpack("greeting", "hello world")
        result = check_backpack("greeting")
        assert "hello world" in result

    def test_overwrite_key(self):
        put_in_backpack("key", "first")
        put_in_backpack("key", "second")
        result = check_backpack("key")
        assert "second" in result
        assert "first" not in result

    def test_missing_key(self):
        result = check_backpack("nonexistent")
        assert "Nothing found" in result

    def test_empty_string_value(self):
        put_in_backpack("empty", "")
        result = check_backpack("empty")
        assert "Found 'empty'" in result

    def test_count_in_response(self):
        result = put_in_backpack("a", "1")
        assert "1 items" in result
        result = put_in_backpack("b", "2")
        assert "2 items" in result


class TestRummage:
    def test_key_match(self):
        put_in_backpack("project-notes", "some notes")
        result = rummage_backpack("project")
        assert "Key matches" in result
        assert "project-notes" in result

    def test_value_match(self):
        put_in_backpack("mykey", "the secret password is banana")
        result = rummage_backpack("banana")
        assert "Value matches" in result
        assert "mykey" in result

    def test_case_insensitive(self):
        put_in_backpack("Notes", "Important stuff")
        assert "Key matches" in rummage_backpack("notes")
        assert "Value matches" in rummage_backpack("IMPORTANT")

    def test_no_matches(self):
        put_in_backpack("a", "b")
        result = rummage_backpack("zzz")
        assert "Found nothing" in result

    def test_key_match_not_duplicated_in_values(self):
        put_in_backpack("banana", "banana")
        result = rummage_backpack("banana")
        assert "Key matches" in result
        assert "Value matches" not in result


class TestListContents:
    def test_empty(self):
        result = list_contents()
        assert "0 items" in result

    def test_lists_keys(self):
        put_in_backpack("x", "1")
        put_in_backpack("y", "2")
        result = list_contents()
        assert "2 items" in result
        assert "x" in result
        assert "y" in result


class TestTossOut:
    def test_delete_existing(self):
        put_in_backpack("temp", "data")
        result = toss_out("temp")
        assert "Threw away" in result
        assert "Nothing found" in check_backpack("temp")

    def test_delete_missing(self):
        result = toss_out("ghost")
        assert "Item not found" in result


class TestPackUnpack:
    def test_round_trip(self, tmp_project):
        put_in_backpack("alpha", "one")
        put_in_backpack("beta", "two")

        result = pack_for_travel()
        assert "Packed 2" in result

        # Verify JSON file was created
        json_path = os.path.join(str(tmp_project), "backpack.json")
        assert os.path.exists(json_path)
        with open(json_path) as f:
            data = json.load(f)
        assert data == {"alpha": "one", "beta": "two"}

        # Clear the cache, then unpack
        toss_out("alpha")
        toss_out("beta")
        assert "0 items" in list_contents()

        result = unpack_from_travel()
        assert "Unpacked 2" in result
        assert "one" in check_backpack("alpha")
        assert "two" in check_backpack("beta")

    def test_unpack_missing_file(self):
        result = unpack_from_travel()
        assert "No 'backpack.json' found" in result


class TestProjectRootDetection:
    @pytest.fixture(autouse=True)
    def restore_real_paths(self, monkeypatch):
        """Undo the autouse fixture so we test the real get_project_paths."""
        monkeypatch.setattr(server, "get_project_paths", _real_get_project_paths)

    def test_finds_git_root(self, tmp_path, monkeypatch):
        os.makedirs(tmp_path / "sub" / "deep")
        (tmp_path / ".git").mkdir()
        monkeypatch.chdir(tmp_path / "sub" / "deep")
        monkeypatch.delenv("BACKPACK_DIR", raising=False)
        root, memory_dir = server.get_project_paths()
        assert root == str(tmp_path)
        assert memory_dir == os.path.join(str(tmp_path), ".backpack_memory")

    def test_finds_pyproject_root(self, tmp_path, monkeypatch):
        os.makedirs(tmp_path / "child")
        (tmp_path / "pyproject.toml").write_text("")
        monkeypatch.chdir(tmp_path / "child")
        monkeypatch.delenv("BACKPACK_DIR", raising=False)
        root, _ = server.get_project_paths()
        assert root == str(tmp_path)

    def test_falls_back_to_cwd(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("BACKPACK_DIR", raising=False)
        root, _ = server.get_project_paths()
        assert root == str(tmp_path)

    def test_env_var_override(self, tmp_path, monkeypatch):
        custom_dir = tmp_path / "custom"
        custom_dir.mkdir()
        monkeypatch.setenv("BACKPACK_DIR", str(custom_dir))
        root, memory_dir = server.get_project_paths()
        assert root == str(custom_dir)
        assert memory_dir == os.path.join(str(custom_dir), ".backpack_memory")


# Import tool functions directly for cleaner test calls
from mcp_backpack.server import (
    put_in_backpack,
    check_backpack,
    rummage_backpack,
    list_contents,
    toss_out,
    pack_for_travel,
    unpack_from_travel,
)
