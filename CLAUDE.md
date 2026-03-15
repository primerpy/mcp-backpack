# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP Backpack is a persistent, portable memory tool for Claude Code and MCP clients. It's an MCP server that exposes key-value storage tools backed by diskcache, with import/export to JSON for git portability.

## Development Commands

```bash
# Install dependencies
uv sync

# Run the MCP server directly
uv run mcp-backpack

# Run without the CLI entry point
uv run python -m mcp_backpack.server
```

Uses Python 3.14, uv for package management, and hatchling as the build backend.

## Architecture

Single-module MCP server in `src/mcp_backpack/server.py`. All tool definitions live in this file using the `FastMCP` decorator pattern (`@mcp.tool()`).

**Storage**: diskcache-backed key-value store. Each project gets its own `.backpack_memory/` directory (based on `os.getcwd()` at runtime).

**Portability**: `pack_for_travel` exports to `backpack.json` (committable), `unpack_from_travel` imports it back into diskcache.

**Entry point**: `mcp-backpack` CLI command defined in `pyproject.toml` → `mcp_backpack.server:main` → `mcp.run()`.

## Git Commit Rules

- PrimerPy is the sole developer and author of all commits.

**Auto-compact prep**: `prepare_for_compaction` and `restore_session` tools handle context survival. Internal keys prefixed with `_config:` and `_session:` are excluded from user-facing listings.

## Auto-Compact Behavior

When MCP Backpack is connected, Claude should follow these rules automatically:

1. **Session start**: Call `restore_session` to load the latest recap and pinned keys.
2. **Before compaction**: When context is running long or compaction is imminent, call `prepare_for_compaction` with a summary of: what was worked on, key decisions, current state, and next steps.
3. **Pinned keys**: Important persistent context (architecture notes, project conventions, active task info) should be pinned via `pin_key` so they survive across sessions automatically.
