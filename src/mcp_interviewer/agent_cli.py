"""CLI for the MCP Interviewer Agent."""

import argparse
import asyncio
import logging
import sys

from .agent import AgentConfig, AgentRunner


def cli():
    """Main CLI entry point for mcp-interviewer-agent."""
    parser = argparse.ArgumentParser(
        description="Automatically improve MCP servers by creating FastMCP proxy servers"
    )

    parser.add_argument(
        "server_command",
        help="Command to run the MCP server (e.g., 'npx @org/mcp-server-foo')",
    )

    parser.add_argument(
        "--output",
        "-o",
        default="./agent_workspace/server.py",
        help="Full path where the improved server will be written (default: ./agent_workspace/server.py). The parent directory becomes the working directory.",
    )

    parser.add_argument(
        "--max-turns",
        type=int,
        default=100,
        help="Maximum number of agent turns before stopping (default: 100)",
    )

    parser.add_argument(
        "--model",
        default="gpt-4o",
        help="OpenAI model to use (default: gpt-4o)",
    )

    parser.add_argument(
        "--max-bash-output",
        type=int,
        default=50000,
        help="Maximum bash output characters (default: 50000)",
    )

    parser.add_argument(
        "--max-file-read",
        type=int,
        default=100000,
        help="Maximum file read characters (default: 100000)",
    )

    parser.add_argument(
        "--existing-report",
        help="Path to existing mcp-interview.md file (skips initial analysis)",
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARN", "ERROR"],
        help="Logging level (default: INFO)",
    )

    parser.add_argument(
        "--client",
        default="openai.OpenAI",
        help="Import path to OpenAI client (default: openai.OpenAI)",
    )

    parser.add_argument(
        "--client-kwargs",
        nargs="+",
        default=[],
        help="key=value pairs for client constructor",
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Suppress httpx INFO logs (only show warnings and errors)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    # Parse output path to determine work_dir and filename
    from pathlib import Path

    output_path = Path(args.output)
    work_dir = str(output_path.parent)
    output_filename = output_path.name

    # Create config
    config = AgentConfig(
        max_bash_output_chars=args.max_bash_output,
        max_file_read_chars=args.max_file_read,
        max_turns=args.max_turns,
        model=args.model,
        output_filename=output_filename,
        work_dir=work_dir,
        existing_report_file=args.existing_report,
    )

    # Initialize OpenAI client
    import importlib

    module_path, class_name = args.client.rsplit(".", 1)
    module = importlib.import_module(module_path)
    client_class = getattr(module, class_name)

    # Parse client kwargs
    client_kwargs = {}
    for kwarg in args.client_kwargs:
        if "=" not in kwarg:
            raise ValueError(f"Client kwarg must be in key=value format: {kwarg}")
        key, value = kwarg.split("=", 1)
        # Try to convert value to appropriate type
        if value.lower() in ("true", "false"):
            value = value.lower() == "true"
        elif value.isdigit():
            value = int(value)
        elif value.replace(".", "").isdigit():
            value = float(value)
        client_kwargs[key] = value

    client = client_class(**client_kwargs)

    # Run agent
    try:
        runner = AgentRunner(config, client)
        result_path = asyncio.run(runner.run(args.server_command))
        print(f"\n✅ Success! Improved server written to: {result_path}")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        logging.exception("Agent failed")
        sys.exit(1)


if __name__ == "__main__":
    cli()
