from shared.mcp_client import MCPClient


def test_mcp_client():
    client = MCPClient()

    response = client.generate(
        """
        Say hello.

        Reply with only:

        Hello AI Studio
        """
    )

    print("Response from MCP Client:")
    print(response)

    assert response is not None


if __name__ == "__main__":
    test_mcp_client()