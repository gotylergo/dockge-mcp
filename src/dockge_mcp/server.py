from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
import asyncio
from .client import (
    call_dockge_api,
    dockge_client,
    rest_get_history,
    rest_get_stack,
    rest_list_stacks,
    rest_stack_action,
)
from .settings import settings

mcp = FastMCP(name="DockgeMCP")


async def _call_dockge_and_check(event_name: str, *args, **kwargs):
    """
    Helper to call Dockge and return the result, successful or not.
    """
    return await call_dockge_api(event_name, *args, **kwargs)


async def _execute_stack_action(event_name: str, stack_name: str, endpoint: str, *args) -> dict:
    """
    A helper to wrap stack actions that produce terminal output or run via REST API.
    """
    if settings.dockge_api_token and not endpoint:
        action_map = {
            "startStack": "start",
            "stopStack": "stop",
            "restartStack": "restart",
            "updateStack": "update",
        }
        if event_name in action_map:
            try:
                return await rest_stack_action(stack_name, action_map[event_name])
            except Exception as e:
                return {"ok": False, "msg": f"Failed to perform {action_map[event_name]} on {stack_name}: {e}"}

    terminal_name = f"compose-{endpoint}-{stack_name}"
    try:
        await dockge_client.start_log_session(terminal_name)
    except Exception as e:
        return {"ok": False, "msg": f"Unable to start log session: {e}"}

    api_args = (stack_name,) + args
    response = await call_dockge_api(event_name, *api_args, endpoint=endpoint)
    response["terminal_name"] = terminal_name

    if response.get("ok"):
        response["msg"] = (
            f"'{event_name}' action started. Track logs using get_terminal_logs "
            f"with terminal_name: '{terminal_name}'"
        )

    return response


@mcp.tool
async def deploy_stack(name: str, composeYAML: str, composeENV: str, isAdd: bool, endpoint: str = "") -> dict:
    """
    Deploys a Docker Compose stack in a remote server.
    Args:
        name: The name of the stack.
        composeYAML: The content of the compose.yaml file.
        composeENV: The content of the .env file.
        isAdd: True if this is a new stack, False if modifying an existing one.
        endpoint: The endpoint specifies which remote server to run the action on.
    Returns:
        A dictionary containing the 'terminal_name' to be used with 'get_terminal_logs' to see the tool result.
    """
    return await _execute_stack_action("deployStack", name, endpoint, composeYAML, composeENV, isAdd)


@mcp.tool
async def save_stack(name: str, composeYAML: str, composeENV: str, isAdd: bool, endpoint: str = "") -> dict:
    """
    Saves the Docker Compose stack files (`compose.yaml` and `.env`) in a remote server without deploying it.
    Args:
        name: The name of stack.
        composeYAML: The content of the compose.yaml file.
        composeENV: The content of the .env file.
        isAdd: True if this is a new stack, False if modifying an existing one.
        endpoint: The endpoint specifies which remote server to run the action on.
    Returns:
        A dictionary confirming the action was successful.
    """
    return await _call_dockge_and_check("saveStack", name, composeYAML, composeENV, isAdd, endpoint=endpoint)


@mcp.tool
async def delete_stack(name: str, endpoint: str = "") -> dict:
    """
    Stops the Docker Compose stack, remove all orphaned containers, deletes the compose and evn yaml files in the remote server.
    Args:
        name: The name of the stack to delete.
        endpoint: The endpoint specifies which remote server to run the action on.
    Returns:
        A dictionary containing the 'terminal_name' to be used with 'get_terminal_logs' to see tool result.
    """
    return await _execute_stack_action("deleteStack", name, endpoint)


@mcp.tool
async def start_stack(stackName: str, endpoint: str = "") -> dict:
    """
    Start a stopped Docker Compose stack on a remote server.
    Args:
        stackName: The name of the stack to start.
        endpoint: The endpoint specifies which remote server to run the action on.
    Returns:
        A dictionary containing the 'terminal_name' to be used with 'get_terminal_logs' to see the tool result.
    """
    return await _execute_stack_action("startStack", stackName, endpoint)


@mcp.tool
async def stop_stack(stackName: str, endpoint: str = "") -> dict:
    """
    Stops a running Docker Compose stack on a remote server.
    Args:
        stackName: The name of the stack to stop.
        endpoint: The endpoint specifies which remote server to run the action on.
    Returns:
        A dictionary containing the 'terminal_name' to be used with 'get_terminal_logs' to see the tool result.
    """
    return await _execute_stack_action("stopStack", stackName, endpoint)


@mcp.tool
async def restart_stack(stackName: str, endpoint: str = "") -> dict:
    """
    Restart a Docker Compose stack on a remote server.
    Args:
        stackName: The name of the stack to restart.
        endpoint: The endpoint specifies which remote server to run the action on.
    Returns:
        A dictionary containing the 'terminal_name' to be used with 'get_terminal_logs' to see the tool result.
    """
    return await _execute_stack_action("restartStack", stackName, endpoint)


@mcp.tool
async def update_stack(stackName: str, endpoint: str = "") -> dict:
    """
    Runs docker compose full to update images for given stack running in a remote server and redeploys it.
    Args:
        stackName: The name of the stack to update.
        endpoint: The endpoint specifies which remote server to run the action on.
    Returns:
        A dictionary containing the 'terminal_name' to be used with 'get_terminal_logs' to see the tool result.
    """
    return await _execute_stack_action("updateStack", stackName, endpoint)


@mcp.tool
async def get_stack(stackName: str, endpoint: str = "") -> dict:
    """
    Retrieves the configuration and status of a single Docker Compose stack.
    Args:
        stackName: The name of the stack to retrieve.
        endpoint: The endpoint specifies which remote server to run the action on.
    """
    if settings.dockge_api_token and not endpoint:
        try:
            return await rest_get_stack(stackName)
        except Exception as e:
            return {"ok": False, "msg": f"Failed to get stack {stackName}: {e}"}
    return await _call_dockge_and_check("getStack", stackName, endpoint=endpoint)


@mcp.tool
async def list_stacks() -> dict:
    """Retrieves the list of Docker Compose stacks from the Dockge server."""
    if settings.dockge_api_token:
        try:
            return await rest_list_stacks()
        except Exception as e:
            return {"ok": False, "msg": f"Failed to list stacks: {e}"}
    return await _call_dockge_and_check("requestStackList")


@mcp.tool
async def get_stack_service_status(stackName: str, endpoint: str = "") -> dict:
    """
    Fetches the real-time status of services within a Docker Compose stack from a remote server.
    Args:
        stackName: The name of the stack to inspect.
        endpoint: The endpoint specifies which remote server to run the action on.
    """
    return await _call_dockge_and_check("serviceStatusList", stackName, endpoint=endpoint)


@mcp.tool
async def get_docker_network_list() -> dict:
    """Retrieves a list of all Docker networks from a remote server."""
    return await _call_dockge_and_check("getDockerNetworkList")


async def _execute_interactive_action(stack_name: str, service_name: str, endpoint: str, shell: str) -> dict:
    """
    A helper to wrap starting an interactive terminal.

    It constructs the terminal name, starts a log session, executes the command,
    and returns the terminal name for log retrieval, for both success and failure cases.
    """
    # 1. Construct the terminal name.
    terminal_name = f"container-exec-{endpoint}-{stack_name}-{service_name}-0"

    # 2. Start the log session in the client.
    await dockge_client.start_log_session(terminal_name)

    # 3. Trigger the actual action on the Dockge server.
    response = await dockge_client.start_interactive_terminal(stack_name, service_name, endpoint, shell)

    # 4. Add the terminal name to the response in all cases.
    response["terminal_name"] = terminal_name

    # 5. If the call was successful, update the message.
    if response.get("ok"):
        response["msg"] = (
            f"'interactiveTerminal' action started. Track logs using get_terminal_logs "
            f"with terminal_name: '{terminal_name}'"
        )

    # For failures, the original 'msg' from Dockge is preserved.
    return response


@mcp.tool
async def start_remote_terminal(stack_name: str, service_name: str, endpoint: str = "", shell: str = "bash") -> dict:
    """
    Starts an interactive terminal session for a service in a Docker Compose stack running in a remote server.
    Args:
        stack_name: The name of the stack the service belongs to.
        service_name: The name of the service to start the terminal for.
        endpoint: The endpoint specifies which remote server to run the action on.
        shell: The shell to use (e.g., "bash", "sh"). Defaults to "bash".
    Returns:
        A dictionary containing the 'terminal_name' to be used with 'send_terminal_input' and 'get_terminal_logs'.
    """
    return await _execute_interactive_action(stack_name, service_name, endpoint, shell)

@mcp.tool
async def send_remote_command(terminal_name: str, command: str, endpoint: str = "") -> dict:
    """
    Sends a command to a remote interactive terminal session started by 'start_remote_terminal'.
    Use bashful commands like 'ls', 'cd', 'cat', etc. to interact with the service's container.
    Use heredoc syntax (<<EOF ... EOF), sed, or echo with redirection (>>) to create or modify files.
    Long running commands may not return output until they complete.
    Send SIGINT (Ctrl+C) to stop a running command. Repeat if you don't see log updates.
    After sending input, the updated terminal screen can be fetched using 'get_terminal_logs'.
    Args:
        terminal_name: The name of the remote terminal session, started by 'start_remote_terminal'.
        command: The command string to send.
        endpoint: The endpoint specifies which remote server to run the action on.
    Returns:
        A dictionary with 'ok' status.
    """
    return await dockge_client.send_terminal_input(terminal_name, command, endpoint)


@mcp.tool
async def get_terminal_logs(terminal_name: str, last_x_lines: int = 50) -> list[str]:
    """
    Fetches the logs for a remote terminal session. A remote terminal session name is provided by tools output like 'deploy_stack' and 'start_interactive_terminal'.
    Also used for remotely fetching combined logs from all services running in a Docker Compose stack using terminal name pattern 'combined-<endpoint>-<stackName'.
    To find the 'stackName' and 'endpoint' for available stacks, use the 'list_stacks' tool.
    Args:
        terminal_name: The full name of the remote terminal session.
        last_x_lines: The number of recent lines to return.
    Returns:
        A list of strings representing the lines in the terminal's buffer.
    """
    return await dockge_client.get_terminal_log_lines(terminal_name, last_x_lines)


@mcp.tool
async def recreate_stack(stackName: str) -> dict:
    """
    Recreates containers for a Docker Compose stack via the Dockge Enhanced REST API.
    Args:
        stackName: The name of the stack to recreate.
    """
    if settings.dockge_api_token:
        try:
            return await rest_stack_action(stackName, "recreate")
        except Exception as e:
            return {"ok": False, "msg": f"Failed to recreate {stackName}: {e}"}
    return {"ok": False, "msg": "recreate_stack requires DOCKGE_API_TOKEN"}


@mcp.tool
async def pull_recreate_stack(stackName: str) -> dict:
    """
    Pulls new container images and recreates a Docker Compose stack via Dockge Enhanced REST API.
    Args:
        stackName: The name of the stack to pull and recreate.
    """
    if settings.dockge_api_token:
        try:
            return await rest_stack_action(stackName, "pull-recreate")
        except Exception as e:
            return {"ok": False, "msg": f"Failed to pull and recreate {stackName}: {e}"}
    return {"ok": False, "msg": "pull_recreate_stack requires DOCKGE_API_TOKEN"}


@mcp.tool
async def backup_stack(stackName: str) -> dict:
    """
    Creates a stack-scoped backup of Compose and environment files via Dockge Enhanced REST API.
    Args:
        stackName: The name of the stack to backup.
    """
    if settings.dockge_api_token:
        try:
            return await rest_stack_action(stackName, "backup")
        except Exception as e:
            return {"ok": False, "msg": f"Failed to backup {stackName}: {e}"}
    return {"ok": False, "msg": "backup_stack requires DOCKGE_API_TOKEN"}


@mcp.tool
async def get_stack_history(stackName: str = "", limit: int = 50, offset: int = 0) -> dict:
    """
    Retrieves stack operation and audit history from the Dockge Enhanced REST API.
    Args:
        stackName: Optional name of the stack to filter history for.
        limit: Maximum number of entries to return (default 50).
        offset: Offset for pagination (default 0).
    """
    if settings.dockge_api_token:
        try:
            return await rest_get_history(stack=stackName, limit=limit, offset=offset)
        except Exception as e:
            return {"ok": False, "msg": f"Failed to get history: {e}"}
    return {"ok": False, "msg": "get_stack_history requires DOCKGE_API_TOKEN"}


def main():
    if settings.mcp_transport == "http":
        import asyncio
        async def _main_http():
            await mcp.run_async(transport="http", host=settings.mcp_host, port=settings.mcp_port)
        asyncio.run(_main_http())
    else:
        # Default to stdio for local MCP runners (OpenCode, Antigravity, Claude, etc.)
        mcp.run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    main()