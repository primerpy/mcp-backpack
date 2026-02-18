# mcp-backpack 🎒

**A persistent, portable memory layer for Claude Code.**

> **Website:** [mcpbackpack.com](http://mcpbackpack.com)

`mcp-backpack` gives your AI agent a "hard drive." It creates a project-scoped database in your working directory, allowing Claude to remember context, architectural decisions, and to-do lists even after you clear the context window or restart your terminal.

Unlike other memory tools, **Backpack is designed for travel.** You can "pack" your memory into a JSON file, commit it to Git, and "unpack" it on a different machine.

## Features

*   **💾 Persist Context:** Save generic thoughts, summaries, and state to a local SQLite database (`.backpack_memory`).
*   **📂 Project Scoped:** Automatically detects which project you are working in and creates a separate memory silo for it.
*   **✈️ Git Syncing:** Export your database to `backpack.json` to share context with your team or sync between your work laptop and home PC.
*   **⚡ Zero Config:** Built on `diskcache` and `mcp`. No running servers or Docker containers required.

## Installation

### Option 1: Install via PyPI (Recommended)
You can add this tool directly to Claude Code using `uvx`.

```bash
claude mcp add backpack -- uvx mcp-backpack
```

### Option 2: Run from Source (Local Development)
If you have cloned this repository and want to run it locally:

```bash
# Assuming you are in the repo root
claude mcp add backpack -- uvx --from . mcp-backpack
```

## Configuration

To prevent committing your local binary database to Git, **you must update your `.gitignore`**.

Run this command in your project root:

```bash
echo ".backpack_memory/" >> .gitignore
```

> **Note:** Do NOT ignore `backpack.json` if you intend to use the syncing feature!

## usage

Once installed, simply talk to Claude. The tool exposes the following capabilities:

### 1. Daily Workflow
*   **Save a thought:** "Put the current API schema in the backpack as `schema:auth`."
*   **Retrieve a thought:** "Check the backpack for `schema:auth`."
*   **Search:** "Rummage through the backpack for anything related to 'database'."
*   **List all:** "List contents of the backpack."

### 2. The "Context Compaction" Protocol
When Claude's context window fills up, use the backpack to save your state before clearing:

> "Before we compact context, please save our current `task:next_steps` and `session:summary` to the backpack."

### 3. Syncing Across Machines (Travel Mode) ✈️
Moving from your work computer to your personal laptop?

1.  **At Work:** "Pack for travel." (Creates `backpack.json`)
2.  **Git:** `git add backpack.json && git commit -m "sync memory" && git push`
3.  **At Home:** `git pull`
4.  **Claude:** "Unpack from travel."

## Tools API

The server exposes the following tools to the LLM:

| Tool | Description |
| :--- | :--- |
| `put_in_backpack` | Saves a key-value pair to the local `.backpack_memory` database. |
| `check_backpack` | Retrieves a specific value by key. |
| `rummage_backpack` | Fuzzy searches keys and values containing a specific string. |
| `list_contents` | Lists all keys currently stored in the project's backpack. |
| `toss_out` | Permanently deletes a key from memory. |
| `pack_for_travel` | Exports the binary database to a human-readable `backpack.json`. |
| `unpack_from_travel` | Imports `backpack.json` into the active memory. |

## License

MIT License
