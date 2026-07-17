from shared.mcp_client import MCPClient

client = MCPClient()

response = client.generate(

"""
Say hello.

Reply with only:

Hello AI Studio

"""

)

print(response)