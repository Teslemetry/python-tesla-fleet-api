"""Local operator commands; approvals and OAuth are never MCP tools."""

import argparse
import asyncio
import json
import logging
import os
import stat
import sys

from mcp_server.auth import login
from mcp_server.commands import CommandJournal
from mcp_server.config import Config
from mcp_server.storage import Store
from tesla_fleet_api.exceptions import TeslaFleetError


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tesla CN single-owner MCP service (POSIX)"
    )
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("login", help="Interactive Tesla OAuth; stop service first")
    approve = sub.add_parser(
        "approve", help="Review and approve one pending command locally"
    )
    approve.add_argument("request_id")
    serve = sub.add_parser("serve")
    serve.add_argument(
        "--transport", choices=("stdio", "streamable-http"), default="streamable-http"
    )
    args = parser.parse_args()
    # The upstream SDK debug logger can log private request/response data.
    logging.getLogger("tesla_fleet_api").setLevel(logging.WARNING)
    try:
        config = Config.from_env()
        store = Store(config.state_dir)
        if args.action == "login":
            with store.lock("service.lock", blocking=False):
                asyncio.run(login(config, store))
        elif args.action == "approve":
            journal = CommandJournal(store)
            print(
                json.dumps(
                    journal.pending(args.request_id), ensure_ascii=True, indent=2
                )
            )
            if (
                input(
                    "Review the exact vehicle and command above. Type APPROVE to allow one submission: "
                )
                != "APPROVE"
            ):
                raise ValueError("Approval cancelled")
            journal.approve(args.request_id)
            print("Approved for one submission before the original expiry.")
        else:
            if config.private_key is not None:
                info = config.private_key.lstat()
                if (
                    not stat.S_ISREG(info.st_mode)
                    or info.st_mode & 0o077
                    or info.st_uid != os.getuid()
                ):
                    raise ValueError(
                        "Signing key must be an existing owner-only regular file"
                    )
            from mcp_server.server import create_http_app, create_server

            if args.transport == "stdio":
                create_server(config).run(transport="stdio")
            else:
                import uvicorn

                app = create_http_app(config)
                uvicorn.run(
                    app,
                    host="127.0.0.1",
                    port=config.port,
                    access_log=False,
                    log_level="warning",
                )
    except (TeslaFleetError, Exception) as error:
        # Error bodies can contain credentials or location; CLI shows only the class.
        print(
            f"Operation stopped ({type(error).__name__}). Check configuration, private file permissions and login state.",
            file=sys.stderr,
        )
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
