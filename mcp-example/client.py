import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.messages import HumanMessage, ToolMessage

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        

    async def connect_to_server(self):
        server_params = StdioServerParameters(
            command="python",
            args=["mcp-git-server.py"],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # Get all available tools
        tools = await load_mcp_tools(self.session)
        print("\nConnected to server with tools:", [tool.name for tool in tools])

        self.llm = ChatOpenAI(model="gpt-4o-mini")
        self.llm_with_tools = self.llm.bind_tools(tools)

    async def process_query(self, query: str) -> str:
        messages = [ HumanMessage(query) ]

        response = self.llm_with_tools.invoke(messages)

        if len(response.tool_calls) > 0:
            messages.append(response)

            for tool_call in response.tool_calls:
                result = await self.session.call_tool(tool_call['name'], tool_call['args'])
                messages.append(ToolMessage(content = result.content[0], tool_call_id = tool_call['id']))

        result = self.llm_with_tools.invoke(messages)

        return result.pretty_print()
    
    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print(response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():

    client = MCPClient()
    try:
        await client.connect_to_server()
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())