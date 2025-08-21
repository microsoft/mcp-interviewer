import argparse


def cli():
    parser = argparse.ArgumentParser()

    parser.add_argument("server_params")
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

    args = parser.parse_args()

    import logging

    logging.basicConfig(level=getattr(logging, args.log_level))

    params = args.server_params.split(" ")
    params_command = params[0]
    params_args = params[1:]

    from .models import ServerParameters

    params = ServerParameters(command=params_command, args=params_args)

    import importlib

    module, client = args.client.rsplit(".")
    module = importlib.import_module(module)
    client = getattr(module, client)

    client = client()

    from .main import main

    main(client, args.model, params, out_dir=args.out_dir)


if __name__ == "__main__":
    cli()
