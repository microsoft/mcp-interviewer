"""Command-line interface for MCP Interviewer."""

import argparse
import asyncio
import datetime
import json
import sys
from pathlib import Path

from autogen_ext.tools.mcp import (
    McpServerParams,
    McpWorkbench,
    SseServerParams,
    StdioServerParams,
    StreamableHttpServerParams,
)

from . import MCPInterviewer


async def run_interview(
    server_configs: list[McpServerParams],
    iterations_per_tool: int = 3,
    output_file: str | None = None,
) -> None:
    """Run MCP interview with given configuration."""

    # Set up workbenches
    workbenches = []
    for config in server_configs:
        try:
            workbench = McpWorkbench(config)
            workbenches.append(workbench)
        except Exception as e:
            print(f"Error creating workbench from config {config}: {e}")
            continue

    if not workbenches:
        print("No valid workbenches created. Exiting.")
        return

    # Run interview
    print(f"Starting interview of {len(workbenches)} MCP servers...")
    print(f"Testing each tool with {iterations_per_tool} iterations...")
    interviewer = MCPInterviewer(workbenches, iterations_per_tool=iterations_per_tool)

    try:
        results = await interviewer.interview()

        # Display results
        print("\n" + "=" * 50)
        print("INTERVIEW RESULTS")
        print("=" * 50)
        print(f"Overall Score: {results.score:.2f}")
        print(f"Analysis: {results.analysis}")
        print(f"Total Tools: {results.total_tools}")
        print(f"Successful Tools: {results.successful_tools}")
        print(f"Success Rate: {results.success_rate:.1%}")

        for server in results.servers:
            print(f"\n--- Server: {server.name} ---")
            print(f"Score: {server.score:.2f}")
            print(f"Analysis: {server.analysis}")
            print(f"Tools ({len(server.tools)}):")

            for tool in server.tools:
                status = "✓" if tool.score > 0.7 else "⚠" if tool.score > 0.3 else "✗"
                print(f"  {status} {tool.name}: {tool.score:.2f} - {tool.analysis}")

                if tool.errors:
                    for error in tool.errors:
                        print(f"    Error: {error}")

                if tool.rewritten:
                    print("    Suggested improvements available")

        # Save to file if requested
        if output_file:
            output_path = Path(output_file)
            if output_path.suffix in (".yaml", ".yml"):
                import yaml  # noqa: I001

                dumps = yaml.safe_dump(results.model_dump(mode="json"))
                output_path.write_text(dumps)
            else:
                output_path.with_suffix(".json").write_text(results.model_dump_json(indent=2))
            print(f"\nResults saved to {output_file}")

    except Exception as e:
        print(f"Error during interview: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="MCP Interviewer - Analyze MCP servers and tools")

    parser.add_argument(
        "--config",
        type=str,
        required=False,
        help="Path to .json file containing Claude Desktop style definition of MCP Servers",
    )
    parser.add_argument(
        "commands",
        type=str,
        nargs="*",
        help="Strings representing commands to launch MCP servers (stdio) or urls to connect to MCP"
        " Servers (streamable http / sse)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Number of test iterations to run per tool (default: 3)",
    )

    parser.add_argument(
        "--output",
        type=str,
        default=f"interview_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        help="Output file for results (JSON or YAML format)",
    )

    args = parser.parse_args()

    # Load servers
    server_configs: list[McpServerParams] = []

    # Process commands if provided
    if args.commands:
        for command in args.commands:
            if command.startswith(("http://", "https://")):
                # Distinguish between SSE and StreamableHttp based on URL suffix
                if command.endswith("/sse"):
                    server_configs.append(SseServerParams(url=command))
                elif command.endswith("/mcp"):
                    server_configs.append(StreamableHttpServerParams(url=command))
                else:
                    # Default to SSE for backward compatibility
                    server_configs.append(SseServerParams(url=command))
            else:
                # stdio server - assume it's a shell command
                command_parts = command.split()
                server_configs.append(
                    StdioServerParams(
                        command=command_parts[0],
                        args=command_parts[1:] if len(command_parts) > 1 else [],
                    )
                )

    # Load from JSON file if provided
    if args.config:
        try:
            config_path = Path(args.config)
            if config_path.exists():
                config_data = json.loads(config_path.read_text())
                if "mcpServers" in config_data:
                    for server_name, server_config in config_data["mcpServers"].items():
                        # Parse different server types from JSON
                        if "command" in server_config:
                            # stdio server
                            command = server_config["command"]
                            args = server_config.get("args", [])

                            server_configs.append(
                                StdioServerParams(
                                    command=command,
                                    args=args,
                                    env=server_config.get("env"),
                                    cwd=server_config.get("cwd"),
                                )
                            )

                        elif "url" in server_config:
                            # Distinguish between SSE and StreamableHttp based on URL suffix
                            url = server_config["url"]
                            if url.endswith("/sse"):
                                server_configs.append(
                                    SseServerParams(
                                        url=url,
                                        headers=server_config.get("headers"),
                                        timeout=server_config.get("timeout", 5),
                                    )
                                )
                            else:
                                server_configs.append(
                                    StreamableHttpServerParams(
                                        url=url,
                                        headers=server_config.get("headers"),
                                        timeout=server_config.get("timeout", 5),
                                    )
                                )
                        else:
                            print(
                                f"Warning: Unknown server config format for "
                                f"{server_name}: {server_config}"
                            )
                else:
                    print(f"Warning: No 'mcpServers' key found in {args.mcpServers}")
            else:
                print(f"Error: Config file {args.mcpServers} not found")
                sys.exit(1)
        except Exception as e:
            print(f"Error loading config file {args.mcpServers}: {e}")
            sys.exit(1)

    if not server_configs:
        print("No server configurations provided. Use positional arguments and/or --config")
        sys.exit(1)

    # Run interview
    asyncio.run(
        run_interview(
            server_configs=server_configs,
            iterations_per_tool=args.iterations,
            output_file=args.output,
        )
    )


if __name__ == "__main__":
    main()
