# ---------------------------------------------------------------------------
# WebHunter CLI
#
# Only one subcommand remains: `server`. WebHunter is a microservice —
# there's no in-process LLM CLI to drive.
#
# Usage:
#   python main.py server --host 0.0.0.0 --port 8000
# ---------------------------------------------------------------------------

import argparse
import logging
import sys

import uvicorn

from totem.config import HOST as DEFAULT_HOST, PORT as DEFAULT_PORT

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-5s  %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("webhunter")


def start_server(args):
    host = args.host or DEFAULT_HOST
    port = args.port or DEFAULT_PORT
    logger.info(f"Starting WebHunter on {host}:{port}")
    uvicorn.run("totem.server:app", host=host, port=port)


def main():
    parser = argparse.ArgumentParser(description="WebHunter — web search + crawling microservice")
    sub = parser.add_subparsers(dest="command", help="Available commands")

    p_server = sub.add_parser("server", help="Start the FastAPI server")
    p_server.add_argument("--host", default=None, help=f"Bind address (default: {DEFAULT_HOST})")
    p_server.add_argument("--port", "-p", type=int, default=None, help=f"Bind port (default: {DEFAULT_PORT})")

    args = parser.parse_args()
    if args.command == "server":
        start_server(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
