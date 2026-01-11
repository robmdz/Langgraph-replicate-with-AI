"""LangGraph agent implementation for file operations."""

from typing import Annotated, Literal, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from file_agent.config import config
from file_agent.file_ops import create_file, delete_file, edit_file, list_directory, show_file
from file_agent.prompts import get_system_prompt


class AgentState(TypedDict):
    """State for the agent graph."""

    messages: Annotated[list[BaseMessage], "The conversation messages"]


# Define tools for the agent
@tool
def create_file_tool(path: str, content: str) -> str:
    """Create a new file with the specified content.

    Args:
        path: Path where the file should be created (relative to current directory).
        content: Content to write to the file.

    Returns:
        Success or error message.
    """
    result = create_file(path, content)
    if result["success"]:
        return result["message"]
    else:
        return f"Error: {result['message']}"


@tool
def edit_file_tool(path: str, content: str, mode: Literal["replace", "append"] = "replace") -> str:
    """Edit an existing file by replacing or appending content.

    Args:
        path: Path to the file to edit (relative to current directory).
        content: Content to add or replace.
        mode: "replace" to overwrite the file, "append" to add at the end.

    Returns:
        Success or error message.
    """
    result = edit_file(path, content, mode)
    if result["success"]:
        return result["message"]
    else:
        return f"Error: {result['message']}"


@tool
def show_file_tool(path: str) -> str:
    """Display the contents of a file.

    Args:
        path: Path to the file to display (relative to current directory).

    Returns:
        File contents or error message.
    """
    result = show_file(path)
    if result["success"]:
        return f"File contents of {result['path']}:\n\n{result['content']}"
    else:
        return f"Error: {result['message']}"


@tool
def delete_file_tool(path: str) -> str:
    """Delete a file. Use this carefully as the operation cannot be undone.

    Args:
        path: Path to the file to delete (relative to current directory).

    Returns:
        Success or error message.
    """
    result = delete_file(path, confirm=True)
    if result["success"]:
        return result["message"]
    else:
        return f"Error: {result['message']}"


@tool
def list_directory_tool(path: str | None = None) -> str:
    """List the contents of a directory.

    Args:
        path: Path to directory to list. If None, lists current directory.

    Returns:
        Directory listing or error message.
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

# Create tool node
tool_node = ToolNode(tools)


def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """Determine whether to continue to tools or end.

    Args:
        state: Current agent state.

    Returns:
        Next node to execute.
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

    Args:
        flags: Optional dictionary of command flags to modify system prompt.

    Returns:
        A compiled LangGraph agent.
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

        Args:
            state: Current agent state.

        Returns:
            Updated state with LLM response.
        """
        messages = state["messages"]

        # Add system message if not present
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=system_prompt)] + messages

        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    # Create graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

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

    Args:
        prompt: User's natural language prompt.
        flags: Optional dictionary of command flags.

    Returns:
        Final response from the agent.
    """
    agent = create_agent(flags)

    # Initialize state
    initial_state: AgentState = {
        "messages": [HumanMessage(content=prompt)],
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
