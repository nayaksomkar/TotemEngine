# ---------------------------------------------------------------------------
# CLI — Command-line interface using argparse.
#
# Subcommands:
#   research   Run a research query and print the report
#   models     List all available LLM providers
#   server     Start the FastAPI REST server
# ---------------------------------------------------------------------------

import argparse
import sys
import logging

from totem.config import SUPPORTED_MODELS
from totem.graph import run_research
from totem.server import app

# Quiet the verbose library loggers
logging.getLogger("langchain").setLevel(logging.WARNING)
logging.getLogger("langgraph").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Clean step-level logging for the user (stdout to match print() ordering)
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("totem")


def print_line(char="="):
    """Print a separator line."""
    print(char * 60)


def do_research(args):
    """Handle the 'research' subcommand: run pipeline and print report."""
    print_line()
    print("  TotemEngine — AI Research Assistant")
    print_line()
    print(f"  Query: {args.query}")
    print(f"  Model: {SUPPORTED_MODELS.get(args.model, {}).get('display', args.model)}")
    print()

    result = run_research(args.query, args.model)

    # Sub-queries
    print_line()
    print("  TOPICS TO RESEARCH")
    print_line()
    for i, sq in enumerate(result.get("sub_queries", []), 1):
        print(f"  {i}. {sq}")

    # Sources crawled
    print_line()
    print("  SOURCES ANALYZED")
    print_line()
    for i, cc in enumerate(result.get("crawled_contents", []), 1):
        print(f"  {i}. {cc['url']}")

    # Individual summaries
    print_line()
    print("  KEY FINDINGS PER SOURCE")
    print_line()
    for i, s in enumerate(result.get("summaries", []), 1):
        first_line = s.strip().split("\n")[0] if s.strip() else ""
        print(f"\n  [{i}] {first_line.replace('**Source:** ','')}")
        for line in s.strip().split("\n")[1:]:
            print(f"     {line}")

    # Final report
    print_line()
    print("  SYNTHESIS")
    print_line()
    print()
    print(result.get("final_summary", "No result generated."))
    print()


def list_models(_):
    """Handle the 'models' subcommand: print all supported providers."""
    print_line()
    print("  Available models:\n")
    for name, info in SUPPORTED_MODELS.items():
        print(f"    {name:12s}  {info['display']}")
    print()


def start_server(args):
    """Handle the 'server' subcommand: launch Uvicorn + FastAPI."""
    import uvicorn
    logger.info(f"Starting server on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)


def main():
    """Entry point: parse CLI args and dispatch to the right handler."""
    parser = argparse.ArgumentParser(
        description="TotemEngine \u2014 AI-powered research assistant"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # --- research subcommand ---
    p_research = sub.add_parser("research", help="Run a research query")
    p_research.add_argument("query", help="Your research question")
    p_research.add_argument(
        "--model", "-m",
        default="mistral",
        choices=list(SUPPORTED_MODELS.keys()),
        help="AI model to use (default: mistral)",
    )

    # --- models subcommand ---
    p_models = sub.add_parser("models", help="List available models")

    # --- server subcommand ---
    p_server = sub.add_parser("server", help="Start the API server")
    p_server.add_argument("--host", default="0.0.0.0", help="Bind address")
    p_server.add_argument("--port", "-p", type=int, default=8000, help="Port")

    # Parse and dispatch
    args = parser.parse_args()
    if args.command == "research":
        do_research(args)
    elif args.command == "models":
        list_models(args)
    elif args.command == "server":
        start_server(args)
    else:
        parser.print_help()
        sys.exit(1)
