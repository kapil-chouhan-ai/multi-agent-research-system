import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPWebSearchTool:
    """Drop-in replacement for tools.web_search.WebSearchTool. Same public
    interface -- .search(query) -> list[dict] -- but the call is proxied
    through mcp_tools/search_server.py over an MCP stdio transport instead
    of hitting Serper in-process. url_discovery.py needs zero changes;
    main.py just decides which implementation of search_tool to wire in.

    A fresh stdio subprocess is spawned per call. That's wasteful for many
    calls in a tight loop, but keeping the client stateless avoids holding
    a long-lived subprocess + event loop alongside the rest of this
    project's synchronous code, which is the bigger source of bugs in a
    project this size.
    """

    def __init__(self, server_script: str | None = None):
        self.server_script = server_script or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "search_server.py"
        )

    def search(self, query: str) -> list[dict]:
        return asyncio.run(self._search_async(query))

    async def _search_async(self, query: str) -> list[dict]:
        params = StdioServerParameters(command=sys.executable, args=[self.server_script])
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("web_search", {"query": query})
                if result.isError:
                    raise RuntimeError(f"MCP web_search tool returned an error: {result.content}")
                return result.structuredContent.get("result", [])
