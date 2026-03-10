# Scrivener Assistant

A tool that enables AI agents to read and understand [Scrivener](https://www.literatureandlatte.com/scrivener/overview) projects.

It can be run locally as a **Model Context Protocol (MCP)** server for AI clients (like Claude Desktop) to connect to, or used as a standalone **Command Line Interface (CLI)**. The CLI is designed to be easily usable by both humans and AI models directly from the terminal, making debugging much simpler and consuming significantly fewer tokens when prototyping workflows.

## [📖 User Journey & Examples](docs/user_journey.md) - **Start Here!**
Check out our **[User Journey Guide](docs/user_journey.md)** to see a full walkthrough of how to connect, analyze, and automate your writing workflow with reusable prompts.

## Features
*   **Project Connection:** Load any `.scriv` project (Scrivener 3 format).
*   **Binder Navigation:** View the full hierarchy of your draft, research, and notes.
*   **Content Reading:** Read the text content of any document (automatically converted from RTF to plain text).
*   **Safety:** Read-only access ensures your manuscript is never modified.

## Installation

### Prerequisites
*   Python 3.10 or higher
*   `uv` (recommended) or `pip`

### Installation
The easiest way to install Scrivener Assistant is using `pip` directly from the repository.

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the latest version directly from GitHub
pip install git+https://github.com/elnino1/scrivener-assistant.git

# Or install a specific version if preferred:
# pip install git+https://github.com/elnino1/scrivener-assistant.git@v0.1.0
```

Alternatively, you can install a specific release by downloading the `.whl` package from the [GitHub Releases](https://github.com/elnino1/scrivener-assistant/releases) page and running `pip install path/to/downloaded/wheel.whl`.

#### Installing from Source (For Developers)
If you wish to modify the code, clone the repository and install it in editable mode:

```bash
git clone https://github.com/elnino1/scrivener-assistant.git
cd scrivener-assistant
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

This project can be used in two ways: as a **Model Context Protocol (MCP) Server** for AI integrations, or as a standalone **Command Line Interface (CLI)**.

---

### Option 1: Usage as an MCP Server
The primary use case is providing a context bridge for AI clients (like Claude Desktop).

#### Running the Server
You can run the server directly with optional flags:

```bash
# Run with default settings (no project loaded)
python src/server.py

# Load a default project on startup
python src/server.py -p /path/to/my/project.scriv

# Enable verbose debug logging
python src/server.py -p /path/to/my/project.scriv -v
```

**Available Options:**
- `-p, --project PATH`: Path to the .scriv project directory
- `-v, --verbose`: Enable debug logging (default: INFO level)
- `-h, --help`: Show help message

#### Configuration (Claude Desktop)
Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "scrivener": {
      "command": "python3",
      "args": [
        "/absolute/path/to/scrivener-assistant-mcp/src/server.py",
        "-p", "/optional/path/to/project.scriv"
      ]
    }
  }
}
```
*(To enable debug logging, append `"-v"` to the `"args"` array).*

#### Core MCP Tools Exposed
When running as an MCP server, the following fundamental tools are available to the AI:
- `set_project_path(path)`: Sets the active Scrivener project.
- `get_binder_structure()`: Returns the full binder hierarchy as a JSON tree.
- `read_document(uuid)`: Reads the plain text content of a specific document.
*(Note: Dozens of additional tools are exposed for managing metadata, summaries, reviews, character sheets, and location data).*

---

### Option 2: Usage as a CLI
A standalone command-line interface is available for interacting with projects directly from your terminal, without needing an MCP client. This provides direct access to the exact same capabilities as the MCP server. 

> **Tip for AI Workflows:** While designed for humans, AI clients (like Claude) can also be given "skills" or "tool definitions" that allow them to execute these CLI commands. Passing Scrivener context to an AI this way can often be easier to debug and more token-efficient during complex workflows compared to using full MCP integration.

#### Example CLI Commands
```bash
# Get binder structure
scrivener-cli -p /path/to/project.scriv binder

# Read a document
scrivener-cli -p /path/to/project.scriv read <uuid>

# List reusable prompts
scrivener-cli -p /path/to/project.scriv prompt list
```

Run `scrivener-cli --help` for a full list of available commands and subcommands (including metadata, summaries, reviews, characters, locations, etc).

## Development

```bash
# Install dev dependencies
pip install ".[dev]"

# Run tests
pytest
```
