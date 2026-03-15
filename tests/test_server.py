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


class TestPinKey:
    def test_pin_new_key(self):
        result = pin_key("project-notes")
        assert "Pinned 'project-notes'" in result

    def test_pin_duplicate(self):
        pin_key("project-notes")
        result = pin_key("project-notes")
        assert "already pinned" in result

    def test_unpin_existing(self):
        pin_key("project-notes")
        result = unpin_key("project-notes")
        assert "Unpinned 'project-notes'" in result

    def test_unpin_missing(self):
        result = unpin_key("ghost")
        assert "not pinned" in result

    def test_pin_multiple(self):
        pin_key("a")
        pin_key("b")
        result = pin_key("c")
        assert "a" in result
        assert "b" in result
        assert "c" in result


class TestPrepareForCompaction:
    def test_basic_recap(self):
        result = prepare_for_compaction("Working on auth refactor. Next: add tests.")
        assert "Session recap saved" in result
        assert "0 pinned key(s)" in result

    def test_recap_with_pinned_keys(self):
        put_in_backpack("arch", "JWT-based auth")
        pin_key("arch")
        result = prepare_for_compaction("Refactoring auth module.")
        assert "1 pinned key(s)" in result

    def test_recap_overwrites_previous(self):
        prepare_for_compaction("First recap")
        prepare_for_compaction("Second recap")
        result = restore_session()
        assert "Second recap" in result
        assert "First recap" not in result


class TestRestoreSession:
    def test_fresh_start(self):
        result = restore_session()
        assert "Fresh start" in result

    def test_restore_with_recap(self):
        prepare_for_compaction("Fixed 3 bugs, next: deploy")
        result = restore_session()
        assert "Session Recap" in result
        assert "Fixed 3 bugs" in result

    def test_restore_with_pinned_keys(self):
        put_in_backpack("arch", "microservices")
        put_in_backpack("task", "deploy v2")
        pin_key("arch")
        pin_key("task")
        prepare_for_compaction("Working on deploy")
        result = restore_session()
        assert "microservices" in result
        assert "deploy v2" in result

    def test_restore_shows_other_keys(self):
        put_in_backpack("notes", "some notes")
        prepare_for_compaction("Quick session")
        result = restore_session()
        assert "Other keys" in result
        assert "notes" in result

    def test_restore_pinned_only_no_recap(self):
        put_in_backpack("arch", "monolith")
        pin_key("arch")
        result = restore_session()
        assert "No session recap found" in result
        assert "monolith" in result

    def test_internal_keys_hidden_from_other_keys(self):
        put_in_backpack("visible", "yes")
        pin_key("visible")
        prepare_for_compaction("test")
        result = restore_session()
        # _config: and _session: keys should not appear in "Other keys"
        assert "_config:" not in result.split("Other keys")[-1] if "Other keys" in result else True


class TestTTL:
    def test_put_with_ttl(self):
        result = put_in_backpack("bug:123", "some bug", ttl="7d")
        assert "expires in 7d" in result

    def test_put_without_ttl(self):
        result = put_in_backpack("notes", "persistent")
        assert "expires" not in result

    def test_expired_key_removed_on_check(self, monkeypatch):
        put_in_backpack("temp", "data", ttl="1m")
        # Fast-forward time so the key is expired
        from datetime import datetime, timezone, timedelta
        future = datetime.now(timezone.utc) + timedelta(minutes=2)
        monkeypatch.setattr(server, "datetime", type("MockDT", (), {
            "now": staticmethod(lambda tz=None: future),
            "fromisoformat": datetime.fromisoformat,
        }))
        result = check_backpack("temp")
        assert "expired" in result

    def test_unexpired_key_still_accessible(self):
        put_in_backpack("temp", "still here", ttl="7d")
        result = check_backpack("temp")
        assert "still here" in result

    def test_invalid_ttl_format(self):
        try:
            put_in_backpack("bad", "data", ttl="forever")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Invalid TTL" in str(e)

    def test_ttl_survives_pack_unpack(self, tmp_project):
        put_in_backpack("temp", "data", ttl="7d")
        pack_for_travel()
        # Check TTL metadata is in the JSON
        json_path = os.path.join(str(tmp_project), "backpack.json")
        with open(json_path) as f:
            data = json.load(f)
        assert "_config:ttl" in data


class TestBackpackCleanup:
    def test_cleanup_no_expired(self):
        put_in_backpack("perm", "forever")
        result = backpack_cleanup()
        assert "No expired keys" in result
        assert "1 active" in result

    def test_cleanup_removes_expired(self, monkeypatch):
        put_in_backpack("temp", "gone soon", ttl="1m")
        put_in_backpack("perm", "forever")
        # Fast-forward time
        from datetime import datetime, timezone, timedelta
        future = datetime.now(timezone.utc) + timedelta(minutes=2)
        monkeypatch.setattr(server, "datetime", type("MockDT", (), {
            "now": staticmethod(lambda tz=None: future),
            "fromisoformat": datetime.fromisoformat,
        }))
        result = backpack_cleanup()
        assert "Removed 1 expired" in result
        assert "temp" in result


class TestSyncBackpack:
    def test_sync_no_git_repo(self, tmp_project):
        """Sync should gracefully fail if not in a git repo."""
        result = sync_backpack()
        assert "Not a git repository" in result


# Import tool functions directly for cleaner test calls
from mcp_backpack.server import (
    put_in_backpack,
    check_backpack,
    rummage_backpack,
    list_contents,
    toss_out,
    pack_for_travel,
    unpack_from_travel,
    pin_key,
    unpin_key,
    prepare_for_compaction,
    restore_session,
    backpack_cleanup,
    sync_backpack,
)
