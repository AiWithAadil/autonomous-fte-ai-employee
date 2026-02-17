"""
FTE Agent Brain - OpenRouter-powered agent with reasoning loop
"""
import json
from typing import Dict, List, Optional
from openai import OpenAI

from config import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
    OPENROUTER_BASE_URL,
    AGENT_TEMPERATURE,
    AGENT_MAX_TOKENS,
    validate_config
)
from .prompts import SYSTEM_PROMPT, ANALYSIS_PROMPT
from .tools import get_tool_definitions, execute_tool


class FTEAgent:
    """
    Personal AI Employee Agent
    Uses OpenRouter API with tool calling for message analysis
    """

    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize FTE Agent

        Args:
            api_key: OpenRouter API key (defaults to config)
            model: Model to use (defaults to config)
        """
        self.api_key = api_key or OPENROUTER_API_KEY
        self.model = model or OPENROUTER_MODEL

        # Validate configuration
        if not self.api_key:
            validate_config()

        # Initialize OpenAI client with OpenRouter
        self.client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=self.api_key
        )

        # Register tools
        self.tools = get_tool_definitions()

    def analyze_message(self, message: str, sender: str = None) -> Dict:
        """
        Analyze a message using agent reasoning loop

        Args:
            message: The message content to analyze
            sender: Optional sender name

        Returns:
            Dict with structured analysis results
        """
        try:
            # Prepare analysis prompt
            user_prompt = ANALYSIS_PROMPT.format(message=message)

            # Initial agent call with tools
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]

            # Agent reasoning loop
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=AGENT_TEMPERATURE,
                max_tokens=AGENT_MAX_TOKENS
            )

            # Process tool calls
            tool_results = {}
            message_obj = response.choices[0].message

            if message_obj.tool_calls:
                # Execute requested tools
                for tool_call in message_obj.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    # Execute tool
                    result = execute_tool(tool_name, tool_args)
                    tool_results[tool_name] = result

                    # Add tool result to conversation
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tool_call.model_dump()]
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })

                # Get final synthesis from agent
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=AGENT_TEMPERATURE,
                    max_tokens=AGENT_MAX_TOKENS
                )

                synthesis = final_response.choices[0].message.content
            else:
                # No tools called, use direct response
                synthesis = message_obj.content
                tool_results = {}

            # Structure the output
            return self._structure_output(
                message=message,
                sender=sender,
                tool_results=tool_results,
                synthesis=synthesis
            )

        except Exception as e:
            return {
                "error": str(e),
                "message": message,
                "sender": sender
            }

    def _structure_output(
        self,
        message: str,
        sender: Optional[str],
        tool_results: Dict,
        synthesis: str
    ) -> Dict:
        """
        Structure agent output into clean format

        Args:
            message: Original message
            sender: Message sender
            tool_results: Results from tool calls
            synthesis: Agent's final synthesis

        Returns:
            Structured output dict
        """
        output = {
            "message": message,
            "sender": sender or "Unknown",
            "analysis": synthesis,
            "summary": None,
            "priority": "MEDIUM",
            "category": "other",
            "suggested_reply": None,
            "tasks": [],
            "actions": []
        }

        # Extract data from tool results
        if "summarizer" in tool_results:
            summary_data = tool_results["summarizer"]
            output["summary"] = summary_data.get("summary", "")

        if "priority_detector" in tool_results:
            priority_data = tool_results["priority_detector"]
            output["priority"] = priority_data.get("priority", "MEDIUM")

        if "categorizer" in tool_results:
            category_data = tool_results["categorizer"]
            output["category"] = category_data.get("category", "other")

        if "reply_suggester" in tool_results:
            reply_data = tool_results["reply_suggester"]
            suggestions = reply_data.get("suggestions", [])
            if suggestions:
                output["suggested_reply"] = suggestions[0]  # Use first suggestion

        if "task_extractor" in tool_results:
            task_data = tool_results["task_extractor"]
            output["tasks"] = task_data.get("tasks", [])

        # Determine recommended actions
        output["actions"] = self._determine_actions(output)

        return output

    def _determine_actions(self, analysis: Dict) -> List[Dict]:
        """
        Determine recommended actions based on analysis

        Args:
            analysis: Analysis results

        Returns:
            List of recommended actions
        """
        actions = []

        # Suggest reply if we have one
        if analysis.get("suggested_reply"):
            actions.append({
                "type": "send_reply",
                "description": "Send suggested reply",
                "data": {
                    "reply": analysis["suggested_reply"],
                    "recipient": analysis["sender"]
                }
            })

        # Create tasks if we found any
        if analysis.get("tasks"):
            for task in analysis["tasks"]:
                actions.append({
                    "type": "create_task",
                    "description": f"Create task: {task}",
                    "data": {
                        "task": task,
                        "priority": analysis["priority"]
                    }
                })

        return actions

    def quick_analyze(self, message: str) -> str:
        """
        Quick analysis without tool calling (faster, simpler)

        Args:
            message: Message to analyze

        Returns:
            Simple text analysis
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Quickly analyze this message:\n\n{message}"}
                ],
                temperature=AGENT_TEMPERATURE,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
