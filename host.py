import os
import asyncio
import dotenv
import httpx
from openai import OpenAI
from contextlib import AsyncExitStack
from typing import Any
from client import MCPClient

dotenv.load_dotenv()

class ChatHost:
    def __init__(self):
        self.mcp_clients: list[MCPClient] = [
            MCPClient("./weather_USA.py"),
            MCPClient("./weather_Israel.py")
        ]
        self.tool_clients: dict[str, tuple[MCPClient, str]] = {}
        self.clients_connected = False
        self.exit_stack = AsyncExitStack()
        
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            http_client=httpx.Client(verify=False)
        )

    async def connect_mcp_clients(self):
        """חיבור לכל שרתי ה-MCP שהוגדרו"""
        if self.clients_connected:
            return
        for client in self.mcp_clients:
            if client.session is None:
                await client.connect_to_server()
        self.clients_connected = True

    async def get_available_tools(self) -> list[dict[str, Any]]:
        """איסוף כל הכלים מכל השרתים המחוברים"""
        await self.connect_mcp_clients()
        self.tool_clients = {}
        available_tools = []

        for client in self.mcp_clients:
            try:
                response = await client.session.list_tools()
                for tool in response.tools:
                    exposed_name = f"{client.client_name}__{tool.name}"
                    self.tool_clients[exposed_name] = (client, tool.name)
                    available_tools.append({
                        "type": "function",
                        "function": {
                            "name": exposed_name,
                            "description": f"[{client.client_name}] {tool.description}",
                            "parameters": tool.inputSchema,
                        }
                    })
            except Exception as e:
                print(f"Warning: Failed to get tools from {client.client_name}: {e}")
        return available_tools

    async def process_query(self, query: str) -> str:
        """עיבוד השאילתה מול GPT-4o ושימוש בכלים במידת הצורך"""
        messages = [{"role": "user", "content": query}]
        final_text = []

        while True:
            tools = await self.get_available_tools()
            
            # קריאה ל-OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto"
            )

            response_message = response.choices[0].message
            messages.append(response_message)

            if response_message.content:
                final_text.append(response_message.content)

            if not response_message.tool_calls:
                break

            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                import json
                tool_args = json.loads(tool_call.function.init_args if hasattr(tool_call.function, 'init_args') else tool_call.function.arguments)

                client, original_tool_name = self.tool_clients[tool_name]
                result = await client.session.call_tool(original_tool_name, tool_args)
                
                final_text.append(f"[מפעיל כלי: {tool_name}]")
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": str(result.content)
                })

        return "\n".join(final_text)

    async def chat_loop(self):
        print("\nMCP Client Started (OpenAI Mode)!")
        print("Type 'quit' to exit.")
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit': break
                if not query: continue
                
                response = await self.process_query(query)
                print("\n" + response)
            except Exception as e:
                print(f"\nchat_loop Error: {e}")

    async def cleanup(self):
        for client in reversed(self.mcp_clients):
            await client.cleanup()
        await self.exit_stack.aclose()

async def main():
    host = ChatHost()
    try:
        await host.chat_loop()
    finally:
        await host.cleanup()

if __name__ == "__main__":
    asyncio.run(main())