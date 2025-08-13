import asyncio
import logging
from pathlib import Path

from openai import OpenAI

from .interviewer import MCPInterviewer
from .models import ServerParameters
from .reports import generate_full_markdown, generate_summary_markdown

logger = logging.getLogger(__name__)


async def amain(
    client: OpenAI, model: str, params: ServerParameters, out_dir=Path(".")
):
    """Asynchronous main function to evaluate an MCP server and generate reports.

    Performs a complete server evaluation and saves the results in multiple formats:
    - Full markdown report (mcp-scorecard.md)
    - Summary markdown report (mcp-scorecard-short.md)
    - Raw JSON data (mcp-scorecard.json)

    Args:
        client: OpenAI client for LLM-based evaluation
        model: Model name to use for evaluation (e.g., "gpt-4")
        params: ServerParameters for the MCP server to evaluate
        out_dir: Directory to save output files (default: current directory)
    """
    interviewer = MCPInterviewer(client, model)
    scorecard = await interviewer.score_server(params)

    path = out_dir / Path("mcp-scorecard.md")
    logger.info(f"Saving full scorecard to {path}")
    with open(path, "w") as fd:
        fd.write(generate_full_markdown(scorecard))

    path = out_dir / Path("mcp-scorecard-short.md")
    logger.info(f"Saving short scorecard to {path}")
    with open(path, "w") as fd:
        fd.write(generate_summary_markdown(scorecard))

    path = out_dir / Path("mcp-scorecard.json")
    logger.info(f"Saving scorecard json data to {path}")
    with open(path, "w") as fd:
        fd.write(scorecard.model_dump_json(indent=2))


def main(client: OpenAI, model: str, params: ServerParameters, out_dir=Path(".")):
    """Synchronous wrapper for the main evaluation function.

    Args:
        client: OpenAI client for LLM-based evaluation
        model: Model name to use for evaluation (e.g., "gpt-4")
        params: ServerParameters for the MCP server to evaluate
    """
    asyncio.run(amain(client, model, params, out_dir))
