"""LangGraph agent implementation for file operations."""

import operator
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolExecutor, ToolInvocation

from file_agent.config import config
from file_agent.file_ops import create_file, delete_file, edit_file, list_directory, show_file
from file_agent.prompts import get_system_prompt


class AgentState(TypedDict):
    """State for the agent graph.

    This TypedDict defines the state structure used throughout the LangGraph workflow.
    The state maintains conversation history and context between agent invocations.

    Attributes:
        messages: List of conversation messages (HumanMessage, AIMessage, ToolMessage, etc.)
            that maintain the full conversation context. This includes user prompts,
            agent responses, and tool execution results.
    """

    messages: Annotated[list[BaseMessage], operator.add]


# Define tools for the agent
@tool
def create_file_tool(path: str, content: str) -> str:
    """Create a new file with the specified content.

    This tool allows the agent to create new files in the current working directory
    or subdirectories. The path is validated to prevent directory traversal attacks,
    and file size is checked against configured limits.

    Args:
        path: Path where the file should be created (relative to current directory).
            Parent directories will be created automatically if they don't exist.
        content: Content to write to the file. Must be UTF-8 encodable.

    Returns:
        A string message indicating success or failure. On success, returns the
        success message from the file operation. On failure, returns an error
        message prefixed with "Error:".

    Note:
        The file path is validated using validate_path() which prevents directory
        traversal attacks. File size must not exceed MAX_FILE_SIZE configuration.
    """
    result = create_file(path, content)
    if result["success"]:
        return result["message"]
    else:
        return f"Error: {result['message']}"


@tool
def edit_file_tool(path: str, content: str, mode: Literal["replace", "append"] = "replace") -> str:
    """Edit an existing file by replacing or appending content.

    This tool allows the agent to modify existing files. The file must exist before
    editing. In append mode, the new content is added with a newline separator.

    Args:
        path: Path to the file to edit (relative to current directory). The file
            must already exist.
        content: Content to add or replace. In replace mode, this becomes the
            entire file content. In append mode, this is added to the end.
        mode: Edit mode - "replace" to overwrite the entire file, "append" to add
            content at the end. Defaults to "replace".

    Returns:
        A string message indicating success or failure. On success, returns the
        success message from the file operation. On failure, returns an error
        message prefixed with "Error:".

    Note:
        The file must exist before editing. File size after edit must not exceed
        MAX_FILE_SIZE configuration. Path validation prevents directory traversal.
    """
    result = edit_file(path, content, mode)
    if result["success"]:
        return result["message"]
    else:
        return f"Error: {result['message']}"


@tool
def show_file_tool(path: str) -> str:
    """Display the contents of a file.

    This tool allows the agent to read and display file contents. The file must
    exist and not exceed the maximum file size limit. The contents are returned
    as a formatted string for the agent to process.

    Args:
        path: Path to the file to display (relative to current directory).
            The file must exist.

    Returns:
        A formatted string containing the file contents prefixed with the file path,
        or an error message prefixed with "Error:" if the operation fails.

    Note:
        File size must not exceed MAX_FILE_SIZE configuration. Path validation
        prevents directory traversal. The file must exist before reading.
    """
    result = show_file(path)
    if result["success"]:
        return f"File contents of {result['path']}:\n\n{result['content']}"
    else:
        return f"Error: {result['message']}"


@tool
def delete_file_tool(path: str) -> str:
    """Delete a file. Use this carefully as the operation cannot be undone.

    This tool allows the agent to permanently delete files. The deletion is
    automatically confirmed (confirm=True) when called through this tool, so
    the agent should use this carefully.

    Args:
        path: Path to the file to delete (relative to current directory).
            The file must exist.

    Returns:
        A string message indicating success or failure. On success, returns the
        success message from the file operation. On failure, returns an error
        message prefixed with "Error:".

    Warning:
        This operation is irreversible. The file will be permanently deleted
        from the filesystem. Use with caution.

    Note:
        Path validation prevents directory traversal. The file must exist before
        deletion. Only files can be deleted, not directories.
    """
    result = delete_file(path, confirm=True)
    if result["success"]:
        return result["message"]
    else:
        return f"Error: {result['message']}"


@tool
def list_directory_tool(path: str | None = None) -> str:
    """List the contents of a directory.

    This tool allows the agent to explore the directory structure. It returns
    a formatted listing of files and subdirectories with their sizes.

    Args:
        path: Path to directory to list. If None, lists the current working
            directory. The path must exist and be a directory.

    Returns:
        A formatted string containing the directory listing with file/directory
        names and sizes, or an error message prefixed with "Error:" if the
        operation fails. Empty directories return a message indicating the
        directory is empty.

    Note:
        Path validation prevents directory traversal. The path must exist and
        be a directory (not a file). Files are displayed with their sizes,
        directories are marked with a folder icon.
    """
    result = list_directory(path)
    if result["success"]:
        items = result["items"]
        if not items:
            return f"Directory {result['path']} is empty."
        lines = [f"Contents of {result['path']}:"]
        for item in items:
            if item["type"] == "file":
                lines.append(f"  📄 {item['name']} ({item['size']})")
            else:
                lines.append(f"  📁 {item['name']}/")
        return "\n".join(lines)
    else:
        return f"Error: {result['message']}"


# Create list of tools
tools = [
    create_file_tool,
    edit_file_tool,
    show_file_tool,
    delete_file_tool,
    list_directory_tool,
]

# Create tool executor
tool_executor = ToolExecutor(tools)


def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """Determine whether to continue to tools or end.

    This function implements the conditional logic for the LangGraph workflow.
    It examines the last message in the conversation to determine if the agent
    has requested tool execution or is ready to end.

    Args:
        state: Current agent state containing the conversation messages.

    Returns:
        "tools" if the last message contains tool calls that need to be executed,
        "end" if the agent has completed its response without tool calls.

    Note:
        This function is used as a conditional edge function in the LangGraph
        workflow. It checks for the presence of tool_calls attribute on the
        last message to determine the next step.
    """
    messages = state["messages"]
    last_message = messages[-1]

    # If there are tool calls, go to tools
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    # Otherwise, end
    return "end"


def create_agent(flags: dict[str, bool] | None = None) -> StateGraph:
    """Create a LangGraph agent for file operations.

    This function initializes and compiles a LangGraph workflow for the file
    operations agent. It sets up the LLM with tools, configures the system prompt,
    and builds the agent graph with appropriate nodes and edges.

    Args:
        flags: Optional dictionary of command flags (e.g., {"brief": True,
            "flashcards": True}) to modify the system prompt. These flags
            customize the agent's behavior for different output formats and
            complexity levels.

    Returns:
        A compiled StateGraph instance ready to be invoked with user prompts.
        The graph includes an agent node and a tools node, with conditional
        edges that route between them based on tool call requirements.

    Raises:
        ValueError: If configuration validation fails (e.g., missing API key).

    Note:
        The agent uses OpenAI's ChatOpenAI model (gpt-4o by default) with tools
        bound to it. The system prompt is customized based on flags. The workflow
        loops between agent and tools nodes until the agent completes without
        requesting tool execution.
    """
    # Validate configuration
    config.validate()

    # Initialize LLM
    llm = ChatOpenAI(
        model=config.openai_model,
        api_key=config.get_openai_api_key(),
        temperature=0.7,
    )

    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)

    # Get system prompt
    system_prompt = get_system_prompt(flags)

    def call_model(state: AgentState) -> AgentState:
        """Call the LLM with the current state.

        This nested function is used as the agent node in the LangGraph workflow.
        It invokes the LLM with the current conversation state.

        Args:
            state: Current agent state containing conversation messages.

        Returns:
            Updated state dictionary with a new message containing the LLM's
            response. The response may include tool calls if the agent decides
            to use tools.

        Note:
            The system prompt should already be in the state from initialization.
            The LLM has tools bound to it, so it can decide to call tools based
            on the conversation context.
        """
        messages = state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def call_tools(state: AgentState) -> AgentState:
        """Execute tool calls from the agent.

        This function processes tool calls from the agent's response and executes
        them using the ToolExecutor. It extracts tool invocations from the last
        message and returns ToolMessages with the results.

        Args:
            state: Current agent state containing conversation messages with tool calls.

        Returns:
            Updated state dictionary with ToolMessages containing tool execution results.
        """
        messages = state["messages"]
        last_message = messages[-1]

        # Extract tool calls and execute them
        tool_messages = []
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                # Extract tool name and arguments
                tool_name = tool_call.get("name") if isinstance(tool_call, dict) else getattr(tool_call, "name", "")
                tool_args = tool_call.get("args") if isinstance(tool_call, dict) else getattr(tool_call, "args", {})
                tool_call_id = tool_call.get("id") if isinstance(tool_call, dict) else getattr(tool_call, "id", "")

                # Create ToolInvocation and execute
                tool_invocation = ToolInvocation(
                    tool=tool_name,
                    tool_input=tool_args,
                )
                result = tool_executor.invoke(tool_invocation)

                # Create ToolMessage with result
                tool_messages.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call_id,
                    )
                )

        return {"messages": tool_messages}

    # Create graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", call_tools)

    # Set entry point
    workflow.set_entry_point("agent")

    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END,
        },
    )

    # Add edge from tools back to agent
    workflow.add_edge("tools", "agent")

    # Compile graph
    return workflow.compile()


def run_agent(prompt: str, flags: dict[str, bool] | None = None) -> str:
    """Run the agent with a user prompt.

    This is the main entry point for executing the agent workflow. It creates
    an agent instance, initializes the state with the user's prompt, runs the
    workflow, and extracts the final response.

    Args:
        prompt: User's natural language prompt describing the desired file
            operation or learning assistance request.
        flags: Optional dictionary of command flags (e.g., {"brief": True,
            "cornell": True}) to customize the agent's behavior and output format.

    Returns:
        The final response string from the agent. This is the content of the
        last message in the conversation, or a string representation if content
        is not available. Returns "No response generated." if no messages are
        present in the final state.

    Raises:
        ValueError: If configuration validation fails (e.g., missing API key).

    Note:
        The agent workflow may execute multiple tool calls in a loop before
        returning the final response. The conversation state is maintained
        throughout the execution, allowing the agent to use tool results in
        subsequent reasoning steps.
    """
    # Get system prompt (needed for initial state)
    system_prompt = get_system_prompt(flags)
    
    agent = create_agent(flags)

    # Initialize state with system message and user prompt
    initial_state: AgentState = {
        "messages": [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt),
        ],
    }

    # Run agent
    final_state = agent.invoke(initial_state)

    # Extract final message
    messages = final_state["messages"]
    if messages:
        last_message = messages[-1]
        if hasattr(last_message, "content"):
            return last_message.content
        return str(last_message)

    return "No response generated."
