# Dockge MCP Server 🐳⚡

A [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server for [Dockge](https://github.com/louislam/dockge) and [Dockge-Enhanced](https://github.com/Aerya/Dockge-Enhanced).

Connect your AI coding assistants (Claude Code, OpenCode, Google Antigravity, Cursor, Windsurf) directly to your self-hosted Docker Compose environment to list stacks, monitor service states, trigger restarts and updates, create backups, view audit histories, and stream container terminal output.

---

## Features

- **Dual-Mode Connectivity**:
  - **REST API Mode (Recommended for Dockge-Enhanced)**: Stateless authentication via `DOCKGE_API_TOKEN`. Supports listing, status checks, stack operations (start, stop, restart, update, recreate, pull-recreate, build-recreate), stack backups, and audit history.
  - **Socket.IO Mode (Vanilla Dockge & Interactive Sessions)**: Authenticates via username and password. Supports real-time container log buffers and interactive remote terminal exec sessions.
- **Fast & Resilient Startup**: Non-blocking `stdio` transport by default, connecting to endpoints lazily without hanging local LLM agent initializations.
- **Stack Lifecycle Management**: Complete control over Docker Compose services without manually SSH-ing into your host machines.

---

## Tool Reference

| Tool | Mode | Description |
| :--- | :--- | :--- |
| `list_stacks` | REST / Socket.IO | Retrieve all Docker Compose stacks and their current status indicators. |
| `get_stack` | REST / Socket.IO | Inspect stack metadata, compose configurations, and status. |
| `start_stack` | REST / Socket.IO | Start stopped container services in a stack. |
| `stop_stack` | REST / Socket.IO | Gracefully stop running container services in a stack. |
| `restart_stack` | REST / Socket.IO | Restart container services for a stack. |
| `update_stack` | REST / Socket.IO | Check for image updates and redeploy stack services. |
| `recreate_stack` | REST | Recreate containers for a given stack. |
| `pull_recreate_stack` | REST | Pull the latest container images and recreate stack containers. |
| `backup_stack` | REST | Create a stack-scoped backup of `compose.yaml`, `.env`, and metadata. |
| `get_stack_history` | REST | Fetch audit trail and execution history logs. |
| `deploy_stack` | Socket.IO | Deploy new or edited `compose.yaml` and `.env` files to a host. |
| `save_stack` | Socket.IO | Save stack definitions without immediately starting containers. |
| `delete_stack` | Socket.IO | Stop containers, purge files, and remove the stack. |
| `get_stack_service_status` | Socket.IO | Retrieve granular per-service health and container runtime metrics. |
| `get_docker_network_list` | Socket.IO | List all Docker networks available on the host. |
| `start_remote_terminal` | Socket.IO | Open an interactive exec bash session inside a container. |
| `send_remote_command` | Socket.IO | Send shell commands to an open container terminal session. |
| `get_terminal_logs` | Socket.IO | Fetch buffered output lines from active terminal or compose actions. |

---

## Configuration

Settings can be provided via environment variables, `.env`, or sourced in `~/.mcp-env`:

| Variable | Required | Description |
| :--- | :--- | :--- |
| `DOCKGE_URL` | No | Base URL of your Dockge instance (defaults to `http://localhost:5001`). |
| `DOCKGE_API_TOKEN` | Recommended | API token generated under **Settings → Automation** in Dockge-Enhanced. |
| `DOCKGE_USERNAME` | Optional | Username for vanilla Dockge or interactive Socket.IO terminal streaming. |
| `DOCKGE_PASSWORD` | Optional | Password for vanilla Dockge or interactive Socket.IO terminal streaming. |
| `MCP_TRANSPORT` | No | Transport protocol: `stdio` (default) or `http`. |
| `MCP_HOST` | No | Host bind address when running in HTTP mode (defaults to `0.0.0.0`). |
| `MCP_PORT` | No | Port when running in HTTP mode (defaults to `8000`). |

---

## Quickstart

### Running directly with `uvx`

```bash
uvx --from git+https://github.com/gotylergo/dockge-mcp.git dockge-server
```

---

## Agent Configuration Examples

### Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "dockge": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/gotylergo/dockge-mcp.git", "dockge-server"],
      "env": {
        "DOCKGE_URL": "http://192.168.0.2:5001",
        "DOCKGE_API_TOKEN": "dge_your_token_here"
      }
    }
  }
}
```

### OpenCode (`opencode.jsonc`)

```jsonc
{
  "mcp": {
    "dockge": {
      "type": "local",
      "command": ["uvx", "--from", "git+https://github.com/gotylergo/dockge-mcp.git", "dockge-server"],
      "environment": {
        "DOCKGE_URL": "http://192.168.0.2:5001",
        "DOCKGE_API_TOKEN": "dge_your_token_here"
      }
    }
  }
}
```

---

## Local Development

```bash
# Clone repository
git clone https://github.com/gotylergo/dockge-mcp.git
cd dockge-mcp

# Install dependencies using uv
uv sync

# Run the MCP server
uv run dockge-server
```

---

## License

[MIT](LICENSE) © [Tyler Justyn](https://github.com/gotylergo)
