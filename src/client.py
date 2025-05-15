import json
import asyncio
import os
from dotenv import load_dotenv
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
from openai import OpenAI
from contextlib import AsyncExitStack


load_dotenv()

class MCPClient:
    def __init__(self):
        self.api_key = os.getenv('deepseek_api_key')
        self.base_url = os.getenv('deepseek_url')
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.session = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self, path):
        commond = 'python'
        server_params = StdioServerParameters(
            command=commond,
            args=[path],
            env=None,
        )
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(stdio, write))
        await self.session.initialize()
        response = await self.session.list_tools()
        tools = response.tools
        print("可用的MCP工具有：", [tool.name for tool in tools])
    
    async def process_query(self, query):
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": query},
        ]
        mcp_tools = await self.session.list_tools()
        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
        } for tool in mcp_tools.tools]
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=available_tools,
        )
        if response.choices[0].finish_reason == 'tool_calls':
            tool_call = response.choices[0].message.tool_calls[0]
            tool_name = tool_call.function.name
            city = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
            if city['cityname']:
                args = {'city': city['cityname']}
            else:
                print('没有输入城市名')
                return
            results = await self.session.call_tool(tool_name, args)
            messages.append(response.choices[0].message.model_dump())
            messages.append({
                "role": "tool",
                "content": results.content[0].text,
                "tool_call_id": tool_call.id
            })
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
            )
            print(response.choices[0].message.content)
        elif response.choices[0].finish_reason == 'stop':
            print(response.choices[0].message.content)
        else:
            print('Other Finish Reason')
    
    async def cleanup(self):
        await self.exit_stack.aclose()


async def main():
    client = MCPClient()
    await client.connect_to_server('./server.py')
    await client.process_query("北京有什么好玩的地方？")
    await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())