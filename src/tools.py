from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List
import math, re, httpx

@dataclass
class ToolResult:
    content: str
    meta: Dict[str, Any]

class Tool:
    name: str = "tool"
    description: str = "A generic tool"
    def run(self, query: str, session: Dict[str, Any]):
        raise NotImplementedError

class CalculatorTool(Tool):
    name = "calculator"
    description = "Safely evaluate basic arithmetic like '2.5 + 7' or 'sqrt(16)'"

    def run(self, query: str, session: Dict[str, Any]):
        # Very small safe eval for arithmetic only
        allowed = {k: getattr(math, k) for k in ("sqrt", "sin", "cos", "tan", "log", "exp")}
        allowed.update({"__builtins__": {}})
        expr = re.sub(r"[^0-9+\-*/()., epxinsotgqlradc]", "", query)  # crude filter
        try:
            val = eval(expr, allowed, {})
            return ToolResult(content=str(val), meta={"expr": expr})
        except Exception as e:
            return ToolResult(content=f"Sorry, I couldn't compute that.", meta={"error": str(e), "expr": expr})

class MemoryTool(Tool):
    name = "memory"
    description = "Store or retrieve small key facts. Patterns: 'remember that X is Y', 'what is X?'"

    def run(self, query: str, session: Dict[str, Any]):
        mem: Dict[str, Any] = session.setdefault("memory", {})
        q = query.lower().strip()

        if q.startswith("remember"):
            m = re.search(r"remember that (.+?) is (.+)", q)
            if m:
                key, val = m.group(1).strip(), m.group(2).strip().rstrip(".")
                mem[key] = val
                return ToolResult(content=f"Okay, I'll remember that {key} is {val}.", meta={"set": {key: val}})
            return ToolResult(content="Tell me what to remember: 'remember that X is Y'.", meta={})

        m = re.search(r"what is (.+)\??$", q)
        if m:
            key = m.group(1).strip()
            if key in mem:
                return ToolResult(content=f"{key} is {mem[key]}.", meta={"get": {key: mem[key]}})
            return ToolResult(content="I don't have that in memory yet.", meta={"missing": key})

        return ToolResult(content="I can remember facts or tell you what I know. Try: 'remember that my name is Sony'.", meta={})

class EchoTool(Tool):
    name = "echo"
    description = "Echo back helpful text (fallback)."

    def run(self, query: str, session: Dict[str, Any]):
        return ToolResult(content=f"You said: {query}", meta={})

class WebSearchTool(Tool):
    name = "websearch"
    description = "Simple DuckDuckGo HTML search (best-effort). Example: 'search: latest AWS Bedrock news'"
    endpoint = "https://duckduckgo.com/html/"
    def run(self, query: str, session: Dict[str, Any]):
        q = query.replace("search:", "").strip()
        try:
            with httpx.Client(timeout=8.0, headers={"User-Agent":"Mozilla/5.0"}) as client:
                r = client.get(self.endpoint, params={"q": q})
                if r.status_code != 200:
                    return ToolResult(content="Search failed.", meta={"status": r.status_code})
                text = r.text
                snippet = re.sub(r"\s+", " ", text)[:600]
                return ToolResult(content=f"Top results snippet: {snippet} ...", meta={"query": q})
        except Exception as e:
            return ToolResult(content="Search not available right now.", meta={"error": str(e), "query": q})

def get_builtin_tools() -> List[Tool]:
    return [CalculatorTool(), MemoryTool(), EchoTool(), WebSearchTool()]
