import argparse
import sys


def cli():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "server_params",
        help="Either the shell command to execute, or the url to connect to.",
    )
    parser.add_argument(
        "--remote-connection-type",
        choices=["sse", "streamable_http"],
        default="streamable_http",
        help="If MCP server is remote, whether to use streamable_http or sse.",
    )
    parser.add_argument(
        "--model",
        help="Model name for LLM-based evaluation (required when using --test or --judge)",
    )
    parser.add_argument(
        "--client",
        default="openai.OpenAI",
        help="Import path to a callable that returns an OpenAI compatible object. Arguments can be set via the --client-kwargs option.",
    )
    parser.add_argument(
        "--client-kwargs",
        default=[],
        nargs="+",
        help="key=value pairs of keyword arguments to the client constructor",
    )
    parser.add_argument("--out-dir", "-o", default=".")
    parser.add_argument(
        "--log-level", default="INFO", choices=["DEBUG", "INFO", "WARN", "ERROR"]
    )
    parser.add_argument(
        "--headers", nargs="*", help="Remote MCP connection headers in KEY=VALUE format"
    )
    parser.add_argument(
        "--timeout", default=5, type=int, help="Remote MCP connection timeout"
    )
    parser.add_argument(
        "--sse-read-timeout",
        default=5,
        type=int,
        help="Remote MCP connection read timeout",
    )
    parser.add_argument(
        "--judge-tools",
        action="store_true",
        help="Enable experimental LLM judging of tools (generates evaluation scores)",
    )
    parser.add_argument(
        "--judge-test",
        action="store_true",
        help="Enable experimental LLM judging of functional tests (generates evaluation scores)",
    )
    parser.add_argument(
        "--judge",
        action="store_true",
        help="Enable all experimental LLM judging operations (equivalent to --judge-tools --judge-test)",
    )
    parser.add_argument(
        "--reports",
        nargs="+",
        help="Specify which reports to include (in order). Can use full names (e.g., interviewer-info, server-info) or shorthand codes (e.g., II, SI, CAP, TS, TCS, FT, CV, T, R, RT, P)",
    )
    parser.add_argument(
        "--no-collapse",
        action="store_true",
        help="Don't use collapsible sections in the report",
    )
    parser.add_argument(
        "--constraints",
        nargs="+",
        help="Specify which constraint violations to check (all enabled by default). Can use full names (e.g., openai-tool-count, openai-name-length, tool-schema-flatness) or shorthand codes (e.g., OTC, ONL, ONP, OTL, TSF, OA)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Enable functional testing of the server",
    )
    parser.add_argument(
        "--accept-risk",
        action="store_true",
        help="Bypass user confirmation of functional test risk.",
    )
    parser.add_argument(
        "--fail-on-warnings",
        action="store_true",
        help="Return non-zero exit code if any constraint violations with WARNING severity are encountered.",
    )

    args = parser.parse_args()

    import logging

    logging.basicConfig(level=getattr(logging, args.log_level))

    from .models import (
        SseServerParameters,
        StdioServerParameters,
        StreamableHttpServerParameters,
    )

    # Parse server-params to determine if it's a URL or command
    server_params_str = args.server_params

    # Check if it's a URL (starts with http:// or https://)
    if server_params_str.startswith(("http://", "https://")):
        # Remote connection
        url = server_params_str

        # Parse headers if provided
        headers = {}
        if args.headers:
            for header in args.headers:
                if "=" in header:
                    key, value = header.split("=", 1)
                    headers[key] = value
                else:
                    raise ValueError(
                        f"Header argument does not match expected KEY=VALUE format: {header}"
                    )

        # Create appropriate remote server parameters
        if args.remote_connection_type == "sse":
            params = SseServerParameters(
                url=url,
                headers=headers if headers else None,
                timeout=args.timeout,
                sse_read_timeout=args.sse_read_timeout,
            )
        else:  # streamable_http
            params = StreamableHttpServerParameters(
                url=url,
                headers=headers if headers else None,
                timeout=args.timeout,
                sse_read_timeout=args.sse_read_timeout,
            )
    else:
        # Local stdio connection - parse as command and args
        import shlex

        params_list = shlex.split(server_params_str)
        params_command = params_list[0]
        params_args = params_list[1:] if len(params_list) > 1 else []

        params = StdioServerParameters(command=params_command, args=params_args)

    # Handle the --judge flag which enables experimental judging operations (disabled by default)
    should_judge_tool = args.judge or args.judge_tools
    should_judge_functional_test = args.judge or args.judge_test

    # Check if model is required but not provided
    requires_llm = args.test or should_judge_tool or should_judge_functional_test
    if requires_llm and not args.model:
        parser.error(
            "--model is required when using --test, --judge, --judge-tools, or --judge-test"
        )

    if args.test:
        print(
            "🚨 MCP Interviewer will make tool call requests to your MCP server. Depending on the server's capabilities this can lead to irreversible outcomes (e.g. deleting files)."
        )
        accept_risk = args.accept_risk
        while not accept_risk:
            input_str = input("Do you accept this risk? y|[n]: ").strip().lower()
            if not input_str or input_str == "n":
                sys.exit(1)
            else:
                accept_risk = input_str == "y"

    # Only initialize client if LLM features are needed
    if requires_llm:
        import importlib

        module, client = args.client.rsplit(".")
        module = importlib.import_module(module)
        client = getattr(module, client)

        client_kwargs = {}
        # Parse client_kwargs from key=value strings
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

        client = client(**client_kwargs)
    else:
        client = None

    from .main import main

    exit_code = main(
        client,
        args.model,
        params,
        out_dir=args.out_dir,
        should_judge_tool=should_judge_tool,
        should_judge_functional_test=should_judge_functional_test,
        should_run_functional_test=args.test,
        custom_reports=args.reports,
        no_collapse=args.no_collapse,
        selected_constraints=args.constraints,
        fail_on_warnings=args.fail_on_warnings,
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    cli()
