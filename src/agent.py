from __future__ import annotations
from typing import Any, Dict, List, Tuple
import os
from .tools import Tool, ToolResult, get_builtin_tools

# Switchable strategy: rule-based tool picker with optional LLM
USE_LLM = bool(os.getenv("OPENAI_API_KEY"))  # Placeholder toggle

class Agent:
    def __init__(self, session: Dict[str, Any], tools: List[Tool] | None = None) -> None:
        self.session = session
        self.tools = tools or get_builtin_tools()
        self.tool_lookup = {t.name: t for t in self.tools}

    def handle(self, message: str) -> Tuple[str, List[str]]:
        """
        Very small agent loop:
        - decide which tool to use
        - run tool
        - format reply
        We avoid exposing chain-of-thought; only return tool outputs.
        """
        used: List[str] = []
        msg = message.strip()

        tool = self.pick_tool(msg)
        if tool:
            result: ToolResult = tool.run(msg, self.session)
            used.append(tool.name)
            reply = self.format_reply(tool.name, result.content)
            # append to history (truncated) for demo
            hist = self.session.setdefault("history", [])
            hist.append({"user": msg, "tool": tool.name, "reply": reply})
            if len(hist) > 20:
                self.session["history"] = hist[-20:]
            return reply, used

        # fallback
        reply = "I'm not sure which tool fits. Try phrasing like 'remember that X is Y' or 'search: <query>'."
        return reply, used

    def pick_tool(self, msg: str) -> Tool | None:
        m = msg.lower()
        if any(k in m for k in ["add", "sum", "+", "-", "*", "/", "sqrt(", "sin(", "cos(", "tan("]):
            return self.tool_lookup.get("calculator")
        if m.startswith("remember") or m.startswith("what is"):
            return self.tool_lookup.get("memory")
        if m.startswith("search:"):
            return self.tool_lookup.get("websearch")
        # default
        return self.tool_lookup.get("echo")

    def format_reply(self, tool_name: str, content: str) -> str:
        if tool_name == "calculator":
            return content
        if tool_name == "memory":
            return content
        if tool_name == "websearch":
            return content
        return content  # echo or others

def get_default_tools() -> List[Tool]:
    return get_builtin_tools()
