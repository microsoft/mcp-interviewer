import argparse


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
    parser.add_argument("--model", required=True)
    parser.add_argument(
        "--client",
        default="openai.OpenAI",
        help="Import path to a parameter-less callable that returns an OpenAI or AsyncOpenAI compatible object",
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

    import importlib

    module, client = args.client.rsplit(".")
    module = importlib.import_module(module)
    client = getattr(module, client)

    client = client()

    from .main import main

    main(client, args.model, params, out_dir=args.out_dir)


if __name__ == "__main__":
    cli()
