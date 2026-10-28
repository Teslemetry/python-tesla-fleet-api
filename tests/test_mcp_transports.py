"""Real MCP initialization/list/call over memory, TCP HTTP, and stdio.

HTTP bearer, Host and Origin rejection are exercised without Tesla network.
"""

import asyncio
import dataclasses
import os
import socket
import sys
import tempfile
import time
from pathlib import Path
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytest.importorskip("mcp")
import httpx
import uvicorn
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.memory import create_connected_server_and_client_session

from mcp_server.commands import CommandJournal
from mcp_server.config import Config
from mcp_server.server import BearerMiddleware, create_http_app, create_server
from mcp_server.service import TeslaService
from mcp_server.storage import Store

VIN = "LRWYGCEK0NC000001"
BEARER = "test-mcp-bearer-only-not-tesla-token-00001"


class MCPTransportTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store(Path(self.temp.name))
        self.config = Config(
            "id", frozenset({VIN}), Path(self.temp.name), bearer_token=BEARER
        )
        self.api = MagicMock()
        vehicle = MagicMock()
        vehicle.list = AsyncMock(
            return_value={"response": [{"vin": VIN, "state": "online"}]}
        )
        self.api.vehicles.createFleet.return_value = vehicle
        self.service = TeslaService(self.api, self.config, CommandJournal(self.store))

    async def check_client(self, client):
        tools = (await client.list_tools()).tools
        self.assertEqual(len(tools), 6)
        self.assertTrue(
            next(
                t for t in tools if t.name == "tesla_get_location"
            ).annotations.readOnlyHint
        )
        self.assertNotIn("ctx", tools[0].inputSchema["properties"])
        result = await client.call_tool("tesla_list_vehicles", {})
        self.assertFalse(result.isError, result)
        self.assertIn(VIN, str(result))
        result = await client.call_tool("tesla_get_location", {"vin": VIN})
        self.assertTrue(result.isError)
        result = await client.call_tool(
            "tesla_wake_vehicle", {"vin": VIN, "request_id": "transport-test-0001"}
        )
        self.assertTrue(result.isError)
        result = await client.call_tool("tesla_get_vehicle_state", {"vin": "../../x"})
        self.assertTrue(result.isError)
        result = await client.call_tool("door_unlock", {"vin": VIN})
        self.assertTrue(result.isError)

    async def test_real_memory_mcp_tool_schema_and_permissions(self):
        server = create_server(self.config, self.service)
        async with create_connected_server_and_client_session(server) as client:
            await self.check_client(client)

    async def test_real_streamable_http_and_security_boundary(self):
        sock = socket.socket()
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
        cfg = dataclasses.replace(self.config, port=port)
        # Use the production app runtime, mocking only its SDK client.
        self.api.refresh_token = "local-test-refresh"
        sdk_patch = patch("mcp_server.server.ManagedOAuth", return_value=self.api)
        sdk_constructor = sdk_patch.start()
        self.addCleanup(sdk_patch.stop)
        app = create_http_app(cfg)
        host = uvicorn.Server(
            uvicorn.Config(app, log_level="critical", access_log=False)
        )
        task = asyncio.create_task(host.serve(sockets=[sock]))
        try:
            async with asyncio.timeout(10):
                while not host.started:
                    await asyncio.sleep(0.01)
            url = f"http://127.0.0.1:{port}/mcp"
            async with httpx.AsyncClient() as client:
                for method in ("GET", "POST", "DELETE"):
                    self.assertEqual(
                        (await client.request(method, url)).status_code, 401
                    )
                    self.assertEqual(
                        (
                            await client.request(
                                method, url, headers={"Authorization": "Bearer wrong"}
                            )
                        ).status_code,
                        401,
                    )
                auth = {
                    "Authorization": f"Bearer {BEARER}",
                    "Accept": "application/json, text/event-stream",
                }
                self.assertEqual(
                    (
                        await client.post(
                            url, headers={**auth, "Host": "attacker.example"}, json={}
                        )
                    ).status_code,
                    421,
                )
                self.assertEqual(
                    (
                        await client.post(
                            url,
                            headers={**auth, "Origin": "https://attacker.example"},
                            json={},
                        )
                    ).status_code,
                    403,
                )
            async with httpx.AsyncClient(
                headers={"Authorization": f"Bearer {BEARER}"}
            ) as http:
                async with streamable_http_client(url, http_client=http) as (
                    read,
                    write,
                    _,
                ):
                    async with ClientSession(read, write) as client:
                        await client.initialize()
                        await self.check_client(client)
                        results = await asyncio.gather(
                            *(
                                client.call_tool("tesla_list_vehicles", {})
                                for _ in range(10)
                            )
                        )
                        self.assertTrue(all(not r.isError for r in results))
                        sdk_constructor.assert_called_once()
                        with self.assertRaises(BlockingIOError):
                            with self.store.lock("service.lock", blocking=False):
                                self.fail(
                                    "HTTP app must retain the process lease between requests"
                                )
        finally:
            host.should_exit = True
            await asyncio.wait_for(task, 10)
            sock.close()

    async def test_stdio_entrypoint_with_private_token_store(self):
        self.store.write(
            "tokens.json",
            {
                "client_id": "id",
                "region": "cn",
                "access_token": "test-local-only",
                "refresh_token": "test-refresh",
                "expires": int(time.time()) + 3600,
            },
        )
        env = {
            **os.environ,
            "TESLA_CLIENT_ID": "id",
            "TESLA_REGION": "cn",
            "TESLA_STATE_DIR": self.temp.name,
            "TESLA_ALLOWED_VINS": VIN,
            "TESLA_TOOLS": "list_vehicles,get_vehicle_state",
            "TESLA_ENABLE_COMMANDS": "false",
        }
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "mcp_server", "serve", "--transport", "stdio"],
            env=env,
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as client:
                await client.initialize()
                self.assertEqual(len((await client.list_tools()).tools), 6)
                # Denied locally, so this subprocess makes no Tesla call.
                result = await client.call_tool("tesla_get_location", {"vin": VIN})
                self.assertTrue(result.isError)

    async def test_http_requires_separate_strong_bearer(self):
        for token in ("", "short", "x" * 31, "x" * 32 + "\n", "中" * 32):
            with self.assertRaises(ValueError):
                BearerMiddleware(
                    create_server(self.config).streamable_http_app(), token
                )
