"""
Tool definitions for FTE Agent
Skills are registered as tools that the agent can invoke
"""
import sys
from pathlib import Path

# Add skills directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "skills"))

from summarizer import summarize_content
from reply_suggester import suggest_reply
from task_extractor import extract_tasks
from priority_detector import detect_priority
from categorizer import categorize_content


def summarizer_tool(content: str) -> dict:
    """
    Summarize message content

    Args:
        content: The message text to summarize

    Returns:
        dict with summary, key_points, keywords
    """
    return summarize_content(content, return_structured=True)


def reply_suggester_tool(content: str, sender: str = None) -> dict:
    """
    Suggest appropriate replies to a message

    Args:
        content: The message text
        sender: Optional sender name

    Returns:
        dict with message_type and suggestions list
    """
    return suggest_reply(content, sender, return_structured=True)


def task_extractor_tool(content: str) -> dict:
    """
    Extract actionable tasks from message

    Args:
        content: The message text

    Returns:
        dict with tasks list
    """
    return extract_tasks(content, return_structured=True)


def priority_detector_tool(content: str) -> dict:
    """
    Detect priority level of message

    Args:
        content: The message text

    Returns:
        dict with priority, confidence, reasoning
    """
    return detect_priority(content, return_structured=True)


def categorizer_tool(content: str) -> dict:
    """
    Categorize message type

    Args:
        content: The message text

    Returns:
        dict with category, confidence, reasoning
    """
    return categorize_content(content, return_structured=True)


# Tool registry for agent
TOOLS = {
    "summarizer": {
        "function": summarizer_tool,
        "description": "Summarize message content into key points",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The message text to summarize"
                }
            },
            "required": ["content"]
        }
    },
    "reply_suggester": {
        "function": reply_suggester_tool,
        "description": "Suggest appropriate replies to the message",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The message text"
                },
                "sender": {
                    "type": "string",
                    "description": "Optional sender name"
                }
            },
            "required": ["content"]
        }
    },
    "task_extractor": {
        "function": task_extractor_tool,
        "description": "Extract actionable tasks from the message",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The message text"
                }
            },
            "required": ["content"]
        }
    },
    "priority_detector": {
        "function": priority_detector_tool,
        "description": "Detect the priority level (HIGH/MEDIUM/LOW) of the message",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The message text"
                }
            },
            "required": ["content"]
        }
    },
    "categorizer": {
        "function": categorizer_tool,
        "description": "Categorize the message type (work/personal/study/finance/other)",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The message text"
                }
            },
            "required": ["content"]
        }
    }
}


def get_tool_definitions():
    """Get OpenAI-compatible tool definitions"""
    tools = []
    for name, spec in TOOLS.items():
        tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": spec["description"],
                "parameters": spec["parameters"]
            }
        })
    return tools


def execute_tool(tool_name: str, arguments: dict) -> dict:
    """Execute a tool by name with given arguments"""
    if tool_name not in TOOLS:
        return {"error": f"Unknown tool: {tool_name}"}

    try:
        tool_func = TOOLS[tool_name]["function"]
        result = tool_func(**arguments)
        return result
    except Exception as e:
        return {"error": str(e)}
