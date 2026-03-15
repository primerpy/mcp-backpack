import os
import json
import subprocess
import re
from datetime import datetime, timezone, timedelta
from diskcache import Cache
from mcp.server.fastmcp import FastMCP

# Initialize the MCP Server
mcp = FastMCP("Backpack")

PROJECT_ROOT_MARKERS = (".git", "pyproject.toml", "package.json", "Cargo.toml", "go.mod")

def _find_project_root(start):
    """Walk up from start looking for a project root marker."""
    current = os.path.abspath(start)
    while True:
        for marker in PROJECT_ROOT_MARKERS:
            if os.path.exists(os.path.join(current, marker)):
                return current
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent

def get_project_paths():
    """
    Determines the project root and memory location.
    Priority: BACKPACK_DIR env var > project root detection > cwd fallback.
    """
    override = os.environ.get("BACKPACK_DIR")
    if override:
        root = os.path.abspath(override)
    else:
        root = _find_project_root(os.getcwd()) or os.getcwd()
    memory_dir = os.path.join(root, ".backpack_memory")
    return root, memory_dir

TTL_CONFIG_KEY = "_config:ttl"


def _parse_ttl(ttl_str: str) -> int:
    """Parse a TTL string like '7d', '24h', '30m' into seconds."""
    match = re.fullmatch(r"(\d+)\s*([dhm])", ttl_str.strip().lower())
    if not match:
        raise ValueError(f"Invalid TTL format: '{ttl_str}'. Use e.g. '7d', '24h', '30m'.")
    amount, unit = int(match.group(1)), match.group(2)
    multiplier = {"d": 86400, "h": 3600, "m": 60}
    return amount * multiplier[unit]


def _check_expired(key: str, cache: Cache) -> bool:
    """Check if a key is expired. Returns True and deletes it if so."""
    ttl_data = json.loads(cache.get(TTL_CONFIG_KEY, "{}"))
    if key not in ttl_data:
        return False
    meta = ttl_data[key]
    created = datetime.fromisoformat(meta["created_at"])
    if datetime.now(timezone.utc) > created + timedelta(seconds=meta["ttl_seconds"]):
        del cache[key]
        del ttl_data[key]
        cache[TTL_CONFIG_KEY] = json.dumps(ttl_data)
        return True
    return False


@mcp.tool()
def put_in_backpack(key: str, value: str, ttl: str = None):
    """Save a memory key-value pair to the local project backpack.
    Optional ttl sets expiration, e.g. '7d', '24h', '30m'."""
    _, memory_dir = get_project_paths()
    with Cache(memory_dir) as cache:
        cache[key] = value
        if ttl:
            ttl_seconds = _parse_ttl(ttl)
            ttl_data = json.loads(cache.get(TTL_CONFIG_KEY, "{}"))
            ttl_data[key] = {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "ttl_seconds": ttl_seconds,
            }
            cache[TTL_CONFIG_KEY] = json.dumps(ttl_data)
        count = len(cache)
    ttl_msg = f" (expires in {ttl})" if ttl else ""
    return f"Saved '{key}'{ttl_msg}. (Backpack now holds {count} items)"

@mcp.tool()
def check_backpack(key: str):
    """Retrieve a specific item from the backpack."""
    _, memory_dir = get_project_paths()
    with Cache(memory_dir) as cache:
        if _check_expired(key, cache):
            return f"'{key}' has expired and was removed."
        value = cache.get(key)

    if value is not None:
        return f"Found '{key}':\n{value}"
    return f"Nothing found in backpack matching '{key}'."

@mcp.tool()
def rummage_backpack(query: str):
    """Search for keys and values containing the query string."""
    _, memory_dir = get_project_paths()
    key_matches = []
    value_matches = []
    with Cache(memory_dir) as cache:
        for k in cache.iterkeys():
            if query.lower() in str(k).lower():
                key_matches.append(k)
            elif query.lower() in str(cache[k]).lower():
                value_matches.append(k)
    if not key_matches and not value_matches:
        return "Found nothing."
    parts = []
    if key_matches:
        parts.append(f"Key matches: {key_matches}")
    if value_matches:
        parts.append(f"Value matches: {value_matches}")
    return "\n".join(parts)

@mcp.tool()
def list_contents():
    """List all keys in the backpack."""
    _, memory_dir = get_project_paths()
    with Cache(memory_dir) as cache:
        keys = list(cache.iterkeys())
    return f"Backpack Contents ({len(keys)} items): {keys}"

@mcp.tool()
def toss_out(key: str):
    """Delete an item from the backpack."""
    _, memory_dir = get_project_paths()
    with Cache(memory_dir) as cache:
        if key in cache:
            del cache[key]
            return f"Threw away '{key}'."
        return "Item not found."

@mcp.tool()
def pack_for_travel():
    """Export memories to 'backpack.json' for git syncing.
    Runs cleanup first to remove expired keys."""
    root_dir, memory_dir = get_project_paths()
    export_path = os.path.join(root_dir, "backpack.json")

    # Clean expired keys before packing
    backpack_cleanup()

    export_data = {}
    with Cache(memory_dir) as cache:
        for k in cache.iterkeys():
            export_data[k] = cache[k]

    with open(export_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, sort_keys=True)

    return f"Packed {len(export_data)} memories into '{export_path}'."

@mcp.tool()
def unpack_from_travel():
    """Import memories from 'backpack.json'."""
    root_dir, memory_dir = get_project_paths()
    import_path = os.path.join(root_dir, "backpack.json")
    
    if not os.path.exists(import_path):
        return "No 'backpack.json' found."
    
    try:
        with open(import_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        with Cache(memory_dir) as cache:
            for k, v in data.items():
                cache[k] = v
                
        return f"Unpacked {len(data)} items into active memory."
    except Exception as e:
        return f"Error unpacking: {str(e)}"

PINNED_KEYS_KEY = "_config:pinned_keys"
SESSION_RECAP_KEY = "_session:recap"


@mcp.tool()
def pin_key(key: str):
    """Pin a key so it's automatically included when restoring a session."""
    _, memory_dir = get_project_paths()
    with Cache(memory_dir) as cache:
        pinned = json.loads(cache.get(PINNED_KEYS_KEY, "[]"))
        if key not in pinned:
            pinned.append(key)
            cache[PINNED_KEYS_KEY] = json.dumps(pinned)
            return f"Pinned '{key}'. Pinned keys: {pinned}"
        return f"'{key}' is already pinned. Pinned keys: {pinned}"


@mcp.tool()
def unpin_key(key: str):
    """Remove a key from the auto-restore pin list."""
    _, memory_dir = get_project_paths()
    with Cache(memory_dir) as cache:
        pinned = json.loads(cache.get(PINNED_KEYS_KEY, "[]"))
        if key in pinned:
            pinned.remove(key)
            cache[PINNED_KEYS_KEY] = json.dumps(pinned)
            return f"Unpinned '{key}'. Pinned keys: {pinned}"
        return f"'{key}' is not pinned. Pinned keys: {pinned}"


@mcp.tool()
def prepare_for_compaction(summary: str):
    """Save a session recap before context compaction. Call this proactively
    when the conversation is getting long or before compaction occurs.
    The summary should capture: what was worked on, key decisions made,
    current state, and next steps."""
    _, memory_dir = get_project_paths()
    recap = {
        "summary": summary,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with Cache(memory_dir) as cache:
        # Save the recap
        cache[SESSION_RECAP_KEY] = json.dumps(recap)
        # Snapshot pinned key values alongside the recap
        pinned = json.loads(cache.get(PINNED_KEYS_KEY, "[]"))
        pinned_snapshot = {}
        for k in pinned:
            val = cache.get(k)
            if val is not None:
                pinned_snapshot[k] = val
        recap["pinned_snapshot"] = pinned_snapshot
        cache[SESSION_RECAP_KEY] = json.dumps(recap)
    return f"Session recap saved at {recap['timestamp']} with {len(pinned_snapshot)} pinned key(s)."


@mcp.tool()
def restore_session():
    """Restore context after compaction or at the start of a new session.
    Returns the latest session recap and all pinned key values."""
    _, memory_dir = get_project_paths()
    with Cache(memory_dir) as cache:
        raw = cache.get(SESSION_RECAP_KEY)
        if not raw:
            # No recap, but still return pinned keys if any
            pinned = json.loads(cache.get(PINNED_KEYS_KEY, "[]"))
            if not pinned:
                return "No session recap or pinned keys found. Fresh start."
            parts = ["No session recap found.\n\nPinned keys:"]
            for k in pinned:
                val = cache.get(k)
                if val is not None:
                    parts.append(f"\n## {k}\n{val}")
            return "\n".join(parts)

        recap = json.loads(raw)
        parts = [
            f"## Session Recap ({recap['timestamp']})\n{recap['summary']}"
        ]

        # Load current pinned key values (fresher than snapshot)
        pinned = json.loads(cache.get(PINNED_KEYS_KEY, "[]"))
        if pinned:
            parts.append("\n## Pinned Keys")
            for k in pinned:
                val = cache.get(k)
                if val is not None:
                    parts.append(f"\n### {k}\n{val}")
                else:
                    parts.append(f"\n### {k}\n(not found)")

        # List remaining keys for awareness
        all_keys = [k for k in cache.iterkeys()
                    if not k.startswith("_config:") and not k.startswith("_session:")]
        if all_keys:
            parts.append(f"\n## Other keys in backpack\n{all_keys}")

    return "\n".join(parts)


@mcp.tool()
def backpack_cleanup():
    """Remove expired keys and report stale ones. Call periodically or before packing."""
    _, memory_dir = get_project_paths()
    expired = []
    with Cache(memory_dir) as cache:
        ttl_data = json.loads(cache.get(TTL_CONFIG_KEY, "{}"))
        now = datetime.now(timezone.utc)
        expired_keys = []
        for key, meta in list(ttl_data.items()):
            created = datetime.fromisoformat(meta["created_at"])
            if now > created + timedelta(seconds=meta["ttl_seconds"]):
                expired_keys.append(key)
        for key in expired_keys:
            if key in cache:
                del cache[key]
            del ttl_data[key]
            expired.append(key)
        if expired_keys:
            cache[TTL_CONFIG_KEY] = json.dumps(ttl_data)
        remaining = len([k for k in cache.iterkeys() if not k.startswith("_config:") and not k.startswith("_session:")])
    parts = [f"Cleanup complete. {remaining} active keys remain."]
    if expired:
        parts.append(f"Removed {len(expired)} expired: {expired}")
    else:
        parts.append("No expired keys found.")
    return "\n".join(parts)


def _run_git(*args, cwd=None):
    """Run a git command and return (success, output)."""
    result = subprocess.run(
        ["git"] + list(args),
        cwd=cwd, capture_output=True, text=True, timeout=30,
    )
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


@mcp.tool()
def sync_backpack():
    """Sync the backpack with git in one step.
    Packs memories → commits backpack.json → pulls remote changes → pushes → unpacks."""
    root_dir, memory_dir = get_project_paths()
    steps = []

    # Check we're in a git repo
    ok, _ = _run_git("rev-parse", "--is-inside-work-tree", cwd=root_dir)
    if not ok:
        return "Not a git repository. Use pack_for_travel/unpack_from_travel manually."

    # Step 1: Pack
    pack_result = pack_for_travel()
    steps.append(f"1. {pack_result}")

    json_path = os.path.join(root_dir, "backpack.json")

    # Step 2: Check if backpack.json has changes
    ok, diff_output = _run_git("diff", "--name-only", "backpack.json", cwd=root_dir)
    ok2, status_output = _run_git("status", "--porcelain", "backpack.json", cwd=root_dir)
    has_changes = bool(diff_output.strip()) or bool(status_output.strip())

    if has_changes:
        # Stage and commit
        _run_git("add", "backpack.json", cwd=root_dir)
        ok, output = _run_git("commit", "-m", "Sync backpack", cwd=root_dir)
        if ok:
            steps.append("2. Committed backpack.json")
        else:
            steps.append(f"2. Commit skipped: {output}")
    else:
        steps.append("2. No local changes to commit")

    # Step 3: Pull remote changes
    ok, output = _run_git("pull", "--rebase", cwd=root_dir)
    if ok:
        steps.append(f"3. Pulled: {output[:100]}")
    else:
        steps.append(f"3. Pull failed: {output[:100]}")
        return "\n".join(steps) + "\nSync incomplete — resolve conflicts and retry."

    # Step 4: Push
    ok, output = _run_git("push", cwd=root_dir)
    if ok:
        steps.append("4. Pushed to remote")
    else:
        steps.append(f"4. Push: {output[:100]}")

    # Step 5: Unpack (in case pull brought changes)
    unpack_result = unpack_from_travel()
    steps.append(f"5. {unpack_result}")

    return "\n".join(steps)


def main():
    """Entry point for the CLI command."""
    mcp.run()

if __name__ == "__main__":
    main()
