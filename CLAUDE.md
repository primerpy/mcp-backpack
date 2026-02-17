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
