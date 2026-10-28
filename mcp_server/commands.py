"""Durable confirmation and duplicate-submission guard, separate from REST."""

import hashlib
import json
import re
import time
from typing import Any

from mcp_server.storage import Store

REQUEST_ID = re.compile(r"[A-Za-z0-9_-]{16,128}\Z")
CONFIRM_SECONDS = 300
MAX_RECORDS = 10000


class CommandJournal:
    def __init__(self, store: Store):
        self.store = store

    def prepare_or_reserve(
        self, request_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        if not REQUEST_ID.fullmatch(request_id):
            raise ValueError(
                "request_id must be 16–128 letters, digits, underscores or hyphens"
            )
        fingerprint = hashlib.sha256(
            json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()
        with self.store.lock("journal.lock"):
            records = self.store.read("commands.json")
            if request_id in records:
                record = records[request_id]
                if record["fingerprint"] != fingerprint:
                    raise ValueError(
                        "request_id is already bound to different arguments"
                    )
                if (
                    record["status"] in {"pending", "approved"}
                    and record["expires"] <= time.time()
                ):
                    record["status"] = "expired"
                if record["status"] == "approved":
                    record["status"] = "reserved"
                    self.store.write("commands.json", records)
                    return {"status": "execute"}
                # A process crash during reserved means delivery is unknown. Never replay.
                return {
                    "status": "unknown"
                    if record["status"] == "reserved"
                    else record["status"],
                    "request_id": request_id,
                }
            for previous_id, previous in records.items():
                if (
                    previous["fingerprint"] == fingerprint
                    and previous["expires"] > time.time()
                    and previous["status"] not in {"expired", "rejected"}
                ):
                    return {
                        "status": "unknown"
                        if previous["status"] == "reserved"
                        else previous["status"],
                        "request_id": previous_id,
                        "duplicate_of": previous_id,
                        "message": "Equivalent command already exists; retain its original request_id.",
                    }
            if len(records) >= MAX_RECORDS:
                raise ValueError("Command journal is full; operator archival required")
            records[request_id] = {
                "fingerprint": fingerprint,
                "payload": payload,
                "expires": time.time() + CONFIRM_SECONDS,
                "status": "pending",
            }
            self.store.write("commands.json", records)
        return {
            "status": "pending",
            "request_id": request_id,
            "expires_in": CONFIRM_SECONDS,
            "message": "A local operator must review and approve this request; then repeat identical arguments and request_id.",
        }

    def pending(self, request_id: str) -> dict[str, Any]:
        with self.store.lock("journal.lock"):
            record = self.store.read("commands.json").get(request_id)
            if (
                not record
                or record["status"] != "pending"
                or record["expires"] <= time.time()
            ):
                raise ValueError("Request is not pending or has expired")
            return record["payload"]

    def approve(self, request_id: str) -> None:
        with self.store.lock("journal.lock"):
            records = self.store.read("commands.json")
            record = records.get(request_id)
            if (
                not record
                or record["status"] != "pending"
                or record["expires"] <= time.time()
            ):
                raise ValueError("Request is not pending or has expired")
            record["status"] = "approved"
            self.store.write("commands.json", records)

    def finish(self, request_id: str, status: str) -> dict[str, Any]:
        with self.store.lock("journal.lock"):
            records = self.store.read("commands.json")
            records[request_id]["status"] = status
            self.store.write("commands.json", records)
        return {"request_id": request_id, "status": status}
