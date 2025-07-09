"""Prompt templates for MCP interviewer analysis and testing."""

from .types import ServerAnalysis, ToolAnalysis


def generate_mock_args_prompt(tool_name: str, tool_description: str, tool_schema: str) -> str:
    """Generate prompt for creating mock arguments for a tool."""
    return f"""
You are helping test an MCP (Model Context Protocol) tool by generating realistic arguments.

Tool: {tool_name}
Description: {tool_description}
Schema: {tool_schema}

Generate realistic mock arguments that would be valid for this tool. If you have 
generated arguments for this tool before, please try to generate different, varied 
arguments this time to test different scenarios. Respond with only a JSON object 
containing the arguments, no additional text.
"""


def generate_tool_analysis_prompt(
    tool_name: str,
    tool_description: str,
    tool_schema: str,
    mock_args: str,
    test_results: str,
    errors: list[str],
) -> str:
    """Generate prompt for analyzing tool test results."""
    return f"""
You are analyzing the results of testing an MCP (Model Context Protocol) tool. 
Based on the test results, provide a concise but comprehensive analysis of the tool's 
quality and functionality.

Tool Information:
- Name: {tool_name}
- Description: {tool_description or "No description provided"}
- Schema: {tool_schema}

Test Results:
- Mock arguments used: {mock_args}
- Test outcomes: {test_results}
- Errors encountered: {errors}

Provide a brief analysis (1-2 sentences) that summarizes:
1. The completeness, specificity, and clarity of the tool's name, description and schema.
2. Its functionality (whether it works as expected)
3. Whether the observed output matches the described/expected output format and content
4. Key strengths and weaknesses
6. Suggests actionable areas for improvement

Be specific and actionable in your assessment.
"""


def generate_server_analysis_prompt(server_name: str, tool_analyses: list[ToolAnalysis]) -> str:
    """Generate prompt for analyzing server performance."""
    if not tool_analyses:
        return f"Server '{server_name}' has no tools to analyze."

    working_tools_count = len([t for t in tool_analyses if t.score > 0.5])
    total_tools = len(tool_analyses)
    average_score = sum(t.score for t in tool_analyses) / len(tool_analyses)

    tool_summary = "\n".join(
        [f"- {tool.name}: {tool.score:.1%} success - {tool.analysis}" for tool in tool_analyses[:5]]
    )
    if len(tool_analyses) > 5:
        tool_summary += "\n..."

    common_issues = "\n".join(
        [f"- {error}" for tool in tool_analyses for error in (tool.errors or [])[:3]]
    )

    return f"""
You are analyzing the performance of an MCP (Model Context Protocol) server based on 
comprehensive tool testing results. Provide a concise but insightful analysis.

Server: {server_name}
Total Tools: {total_tools}
Working Tools (>50% success): {working_tools_count}
Average Success Rate: {average_score:.2%}

Tool Performance Summary:
{tool_summary}

Common Issues:
{common_issues}

Provide a 2-3 sentence analysis that:
1. Summarizes the server's overall performance and reliability
2. Identifies key strengths and weaknesses
3. Suggests actionable areas for improvement

Be specific and focus on practical insights for developers.
"""


def generate_overall_analysis_prompt(server_analyses: list[ServerAnalysis]) -> str:
    """Generate prompt for analyzing the overall MCP ecosystem."""
    if not server_analyses:
        return "No servers analyzed."

    total_servers = len(server_analyses)
    total_tools = sum(len(server.tools) for server in server_analyses)
    working_servers = len([s for s in server_analyses if s.score > 0.7])

    # Calculate overall success rate
    if total_tools > 0:
        total_score = sum(server.score * len(server.tools) for server in server_analyses)
        overall_success_rate = total_score / total_tools
    else:
        overall_success_rate = 0.0

    # Aggregate common issues across all servers
    all_errors = []
    for server in server_analyses:
        for tool in server.tools:
            all_errors.extend(tool.errors or [])

    common_issues = list(set(all_errors))[:5]  # Top 5 unique issues

    server_breakdown = "\n".join(
        [
            f"- {server.name}: {server.score:.1%} success ({len(server.tools)} tools) - "
            f"{server.analysis[:100]}..."
            for server in server_analyses[:8]
        ]
    )
    if len(server_analyses) > 8:
        server_breakdown += "\n..."

    common_issues_text = "\n".join([f"- {issue}" for issue in common_issues])

    return f"""
You are analyzing the overall health and performance of an MCP (Model Context Protocol) 
ecosystem based on comprehensive testing of multiple servers and their tools.

Ecosystem Overview:
- Total Servers: {total_servers}
- Total Tools: {total_tools}
- High-Performing Servers (>70%): {working_servers}
- Overall Success Rate: {overall_success_rate:.2%}

Server Performance Breakdown:
{server_breakdown}

Most Common Issues Across Ecosystem:
{common_issues_text}

Provide a 3-4 sentence executive summary that:
1. Assesses the overall health and maturity of the MCP ecosystem
2. Identifies systemic patterns and key areas for improvement
3. Provides strategic recommendations for ecosystem-wide improvements
4. Highlights any standout servers or concerning trends

Focus on actionable insights for engineering leadership and ecosystem maintainers.
"""
