from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from pydantic import BaseModel
import os

class MenuInput(BaseModel):
    ingredients: list[str]


food_mcp = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=["food_mcp_server/server.py"],
            env={}
        ),
        timeout=60000,
    )
)

prompt = """
You are a creative fusion chef AI.

YOUR TASK:
- Receive ingredients from user
- Call MCP tool to search recipe
- Create a fusion dish
- Return:
    1. Dish name
    2. Fusion style
    3. Cooking steps
    4. Calories

You MUST use MCP tools.
"""

root_agent = Agent(
    model="gemini-2.5-flash",
    name="fusion_food_agent",
    input_schema=MenuInput,
    instruction=prompt,
    tools=[food_mcp],
)
