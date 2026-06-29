import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from tools.web_search import WebSearchTool

load_dotenv()

mcp = FastMCP("research-web-search")
_tool = WebSearchTool(api_key=os.getenv("SERPER_API_KEY"))


@mcp.tool()
def web_search(query: str) -> list[dict]:
    """Search the web via Serper. Returns a list of {title, snippet, url}."""
    return _tool.search(query)


if __name__ == "__main__":
    mcp.run(transport="stdio")
