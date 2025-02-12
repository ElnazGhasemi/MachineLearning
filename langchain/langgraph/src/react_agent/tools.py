"""This module provides example tools for web scraping and search functionality.

It includes a basic Tavily search function (as an example)

These tools are intended as free examples to get started. For production use,
consider implementing more robust and specialized tools tailored to your needs.
"""

from typing import Any, Callable, List, Optional, cast

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import InjectedToolArg
from typing_extensions import Annotated

from react_agent.configuration import Configuration

import subprocess

async def search(
    query: str, *, config: Annotated[RunnableConfig, InjectedToolArg]
) -> Optional[list[dict[str, Any]]]:
    """Search for general web results.

    This function performs a search using the Tavily search engine, which is designed
    to provide comprehensive, accurate, and trusted results. It's particularly useful
    for answering questions about current events.
    """
    configuration = Configuration.from_runnable_config(config)
    wrapped = TavilySearchResults(max_results=configuration.max_search_results)
    result = await wrapped.ainvoke({"query": query})
    return cast(list[dict[str, Any]], result)

def get_current_time(*args, **kwargs):
    """Returns the current time in H:MM AM/PM format."""
    import datetime  # Import datetime module to get current time

    now = datetime.datetime.now()  # Get current time
    return now.strftime("%I:%M %p")  # Format time in H:MM AM/PM format


MAX_COMMAND_OUTPUT_LENGTH = 16000  # Maximum length for command output
MAX_CODEBASE_LENGTH = 64000  # Maximum length for combined file contents

def run_command(command: str, timeout: int = 60) -> str:
    """Execute a command with a timeout"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        output = result.stdout if result.stdout else result.stderr if result.stderr else ""
        
        # Handle truncation if needed
        if len(output) > MAX_COMMAND_OUTPUT_LENGTH:
            truncated_output = output[:MAX_COMMAND_OUTPUT_LENGTH]
            return f"[TRUNCATED OUTPUT - Original length: {len(output)} chars]\n{truncated_output}\n[End of truncated output]"
        
        return output
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"

TOOLS: List[Callable[..., Any]] = [search, get_current_time, run_command]
