import os
import json
from diskcache import Cache
from mcp.server.fastmcp import FastMCP

# Initialize the MCP Server
mcp = FastMCP("Backpack")

def get_project_paths():
    """
    Determines the project root and memory location based on where the command is run.
    """
    cwd = os.getcwd()
    memory_dir = os.path.join(cwd, ".backpack_memory")
    return cwd, memory_dir

@mcp.tool()
def put_in_backpack(key: str, value: str):
    """Save a memory key-value pair to the local project backpack."""
    _, memory_dir = get_project_paths()
    with Cache(memory_dir) as cache:
        cache[key] = value
        count = len(cache)
    return f"Saved '{key}'. (Backpack now holds {count} items)"

@mcp.tool()
def check_backpack(key: str):
    """Retrieve a specific item from the backpack."""
    _, memory_dir = get_project_paths()
    with Cache(memory_dir) as cache:
        value = cache.get(key)
    
    if value:
        return f"Found '{key}':\n{value}"
    return f"Nothing found in backpack matching '{key}'."

@mcp.tool()
def rummage_backpack(query: str):
    """Search for keys containing the query string."""
    _, memory_dir = get_project_paths()
    results = []
    with Cache(memory_dir) as cache:
        for k in cache.iterkeys():
            if query.lower() in str(k).lower():
                results.append(k)
    return f"Found keys: {results}" if results else "Found nothing."

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
    """Export memories to 'backpack.json' for git syncing."""
    root_dir, memory_dir = get_project_paths()
    export_path = os.path.join(root_dir, "backpack.json")
    
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

def main():
    """Entry point for the CLI command."""
    mcp.run()

if __name__ == "__main__":
    main()
