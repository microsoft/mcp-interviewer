"""Basic tests for the MCPInterviewer package."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from autogen_ext.tools.mcp import StdioServerParams
from mcp_interviewer.patch_autogen_ext_mcp import ExtendedMcpWorkbench
from mcp_interviewer import MCPInterviewer, ToolAnalysis
from mcp_interviewer.types import InterviewResults
from trapi.autogen import TrapiChatCompletionClient


@pytest.fixture
def mock_workbench():
    """Create a mock MCP workbench."""
    workbench = AsyncMock()
    workbench.name = "test_server"
    workbench.list_tools.return_value = [
        {
            "name": "test_tool_1",
            "description": "A test tool",
            "inputSchema": {"type": "object", "properties": {}}
        },
        {
            "name": "test_tool_2", 
            "description": "Another test tool",
            "inputSchema": {"type": "object", "properties": {}}
        }
    ]
    workbench.call_tool.return_value = {"result": "success"}
    return workbench


@pytest.fixture
def mock_model_client():
    """Create a mock OpenAI model client."""
    client = MagicMock()
    return client


@pytest.mark.asyncio
async def test_mcp_interviewer_basic_flow(mock_workbench, mock_model_client):
    """Test basic interviewer flow."""
    interviewer = MCPInterviewer([mock_workbench], mock_model_client)
    
    # Run interview
    results = await interviewer.interview(check_tools=True, rewrite_tools=False)
    
    # Verify results structure
    assert isinstance(results, InterviewResults)
    assert results.score >= 0.0
    assert results.score <= 1.0
    assert len(results.servers) == 1
    assert results.servers[0].name == "test_server"
    assert len(results.servers[0].tools) == 2


@pytest.mark.asyncio
async def test_tool_analysis_structure():
    """Test that ToolAnalysis has correct structure."""
    analysis = ToolAnalysis(
        name="test_tool",
        score=0.8,
        analysis="Tool works well",
        errors=["Minor issue"]
    )
    
    assert analysis.name == "test_tool"
    assert analysis.score == 0.8
    assert analysis.analysis == "Tool works well"
    assert analysis.errors is not None and "Minor issue" in analysis.errors


@pytest.mark.asyncio
async def test_interview_without_tool_checking(mock_workbench, mock_model_client):
    """Test interview with tool checking disabled."""
    interviewer = MCPInterviewer([mock_workbench], mock_model_client)
    
    results = await interviewer.interview(check_tools=False, rewrite_tools=False)
    
    # Should still get results but with neutral scores
    assert isinstance(results, InterviewResults)
    assert len(results.servers) == 1
    assert len(results.servers[0].tools) == 2
    
    # All tools should have neutral score since testing is disabled
    for tool in results.servers[0].tools:
        assert tool.score == 0.5


@pytest.mark.asyncio
async def test_empty_workbench_list(mock_model_client):
    """Test interviewer with no workbenches."""
    interviewer = MCPInterviewer([], mock_model_client)
    
    results = await interviewer.interview()
    
    assert isinstance(results, InterviewResults)
    assert len(results.servers) == 0
    assert results.score == 0.0
    assert "No servers analyzed" in results.analysis


@pytest.mark.asyncio
@pytest.mark.slow
async def test_real_duckduckgo_server():
    """Test interviewer with real DuckDuckGo MCP server via Docker."""
    # Configure DuckDuckGo MCP server via Docker
    server_params = StdioServerParams(
        command="docker",
        args=["run", "-i", "--rm", "mcp/duckduckgo"],
        read_timeout_seconds=30
    )
    
    # Use a real model client (TrapiChatCompletionClient with gpt-4o)
    model_client = TrapiChatCompletionClient("gpt-4o")
    
    async with ExtendedMcpWorkbench(server_params=server_params) as workbench:
        # Create interviewer with real workbench
        interviewer = MCPInterviewer([workbench], model_client)
        
        # Run interview with tool checking enabled
        results = await interviewer.interview(check_tools=True, rewrite_tools=False)
        
        # Verify we got meaningful results
        assert isinstance(results, InterviewResults)
        assert len(results.servers) == 1
        assert results.servers[0].name is not None
        assert len(results.servers[0].tools) > 0  # DuckDuckGo should have search tools
        
        # Verify tools have been tested and scored
        for tool in results.servers[0].tools:
            assert tool.name is not None
            assert 0.0 <= tool.score <= 1.0
            assert tool.analysis is not None
            
        # Overall score should be meaningful
        assert 0.0 <= results.score <= 1.0


@pytest.mark.asyncio
async def test_timeout_and_error_handling(mock_model_client):
    """Test that timeouts and errors are handled gracefully."""
    import asyncio
    from unittest.mock import AsyncMock
    
    # Create a workbench that will timeout on list_tools
    timeout_workbench = AsyncMock()
    timeout_workbench.name = "timeout_server"
    
    async def slow_list_tools():
        await asyncio.sleep(35)  # Longer than our 30s timeout
        return []
    
    timeout_workbench.list_tools.side_effect = slow_list_tools
    
    # Create a workbench that will raise an exception
    error_workbench = AsyncMock()
    error_workbench.name = "error_server"
    error_workbench.list_tools.side_effect = Exception("Connection failed")
    
    # Create interviewer with short timeouts for testing
    interviewer = MCPInterviewer(
        [timeout_workbench, error_workbench], 
        mock_model_client,
        tool_timeout=5.0,
        server_timeout=10.0,
        analysis_timeout=5.0
    )
    
    # Run interview - should complete without hanging or crashing
    results = await interviewer.interview(check_tools=True, rewrite_tools=False)
    
    # Verify results structure is intact despite errors
    assert isinstance(results, InterviewResults)
    assert len(results.servers) == 2
    
    # First server should have timed out
    timeout_server = results.servers[0]
    assert timeout_server.name == "timeout_server"
    assert timeout_server.score == 0.0
    assert "timed out" in timeout_server.analysis.lower()
    assert len(timeout_server.tools) == 0
    
    # Second server should have failed with error
    error_server = results.servers[1]
    assert error_server.name == "error_server"
    assert error_server.score == 0.0
    assert "connection failed" in error_server.analysis.lower()
    assert len(error_server.tools) == 0
    
    # Overall analysis should mention failed servers
    assert "failed servers" in results.analysis.lower()


@pytest.mark.asyncio
async def test_tool_timeout_handling(mock_model_client):
    """Test that individual tool timeouts are handled properly."""
    import asyncio
    from unittest.mock import AsyncMock
    
    # Create a workbench with tools that timeout
    workbench = AsyncMock()
    workbench.name = "test_server"
    workbench.list_tools.return_value = [
        {
            "name": "slow_tool",
            "description": "A tool that takes too long",
            "parameters": {"type": "object", "properties": {}}
        }
    ]
    
    async def slow_tool_call(name, args):
        await asyncio.sleep(40)  # Longer than tool timeout
        return {"result": "success"}
    
    workbench.call_tool.side_effect = slow_tool_call
    
    # Create interviewer with short tool timeout
    interviewer = MCPInterviewer(
        [workbench], 
        mock_model_client,
        tool_timeout=5.0,
        server_timeout=30.0,
        analysis_timeout=10.0
    )
    
    # Run interview
    results = await interviewer.interview(check_tools=True, rewrite_tools=False)
    
    # Verify the slow tool was handled gracefully
    assert len(results.servers) == 1
    server = results.servers[0]
    assert len(server.tools) == 1
    
    slow_tool = server.tools[0]
    assert slow_tool.name == "slow_tool"
    assert "timed out" in slow_tool.analysis.lower()
    assert slow_tool.errors is not None
    assert len(slow_tool.errors) > 0
    assert "timeout" in slow_tool.errors[0].lower()


if __name__ == "__main__":
    pytest.main([__file__])
