import argparse
import sys
import logging

from totem.config import SUPPORTED_MODELS
from totem.graph import run_research
from totem.server import app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("totem")


def print_header():
    print("=" * 60)
    print("  TotemEngine — AI-Powered Research Assistant")
    print("=" * 60)
    print()


def do_research(args):
    print_header()
    logger.info(f"Query: {args.query}")
    logger.info(f"Model: {SUPPORTED_MODELS.get(args.model, {}).get('display', args.model)}")
    print()

    result = run_research(args.query, args.model)

    print("\n" + "=" * 60)
    print("  SUB-QUERIES")
    print("=" * 60)
    for i, sq in enumerate(result.get("sub_queries", []), 1):
        print(f"  {i}. {sq}")

    print("\n" + "=" * 60)
    print("  INDIVIDUAL SUMMARIES")
    print("=" * 60)
    for i, s in enumerate(result.get("summaries", []), 1):
        print(f"\n  [{i}]")
        for line in s.strip().split("\n"):
            print(f"     {line}")

    print("\n" + "=" * 60)
    print("  FINAL SYNTHESIS")
    print("=" * 60)
    print()
    print(result.get("final_summary", "No result generated."))
    print()


def list_models(_):
    print_header()
    print("  Available models:\n")
    for name, info in SUPPORTED_MODELS.items():
        print(f"    {name:12s}  {info['display']}")
    print()


def start_server(args):
    import uvicorn
    logger.info(f"Starting server on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)


def main():
    parser = argparse.ArgumentParser(
        description="TotemEngine — AI-powered research assistant"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    p_research = sub.add_parser("research", help="Run a research query")
    p_research.add_argument("query", help="Your research question")
    p_research.add_argument(
        "--model", "-m",
        default="mistral",
        choices=list(SUPPORTED_MODELS.keys()),
        help="AI model to use (default: mistral)",
    )

    p_models = sub.add_parser("models", help="List available models")

    p_server = sub.add_parser("server", help="Start the API server")
    p_server.add_argument("--host", default="0.0.0.0", help="Bind address")
    p_server.add_argument("--port", "-p", type=int, default=8000, help="Port")

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
