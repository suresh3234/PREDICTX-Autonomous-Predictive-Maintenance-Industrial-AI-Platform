import hashlib
import json
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger("PredictX.HITL.AuditTrail")


class ImmutableAuditTrail:
    """
    Cryptographically chained, immutable audit log for human interventions and safety decisions.
    Uses SHA-256 hash chaining to detect unauthorized tampering.
    """

    def __init__(self):
        self.chain: list[dict[str, Any]] = []
        self._init_genesis_block()

    def _init_genesis_block(self):
        genesis = {
            "index": 0,
            "timestamp": "2026-01-01T00:00:00Z",
            "event_type": "GENESIS_AUDIT_BLOCK",
            "actor_id": "SYSTEM",
            "machine_id": "GLOBAL",
            "action": "INIT_AUDIT_TRAIL",
            "details": {},
            "previous_hash": "0" * 64,
            "hash": "",
        }
        genesis["hash"] = self._compute_hash(genesis)
        self.chain.append(genesis)

    def _compute_hash(self, block: dict[str, Any]) -> str:
        block_copy = {k: v for k, v in block.items() if k != "hash"}
        block_string = json.dumps(block_copy, sort_keys=True, default=str)
        return hashlib.sha256(block_string.encode("utf-8")).hexdigest()

    def log_event(
        self,
        event_type: str,
        actor_id: str,
        machine_id: str,
        action: str,
        details: dict[str, Any] | None = None,
        outcome: str = "SUCCESS",
    ) -> dict[str, Any]:
        """
        Appends a new audit record to the cryptographic hash chain.
        """
        prev_block = self.chain[-1]
        new_index = len(self.chain)

        block = {
            "index": new_index,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "actor_id": actor_id,
            "machine_id": machine_id,
            "action": action,
            "details": details or {},
            "outcome": outcome,
            "previous_hash": prev_block["hash"],
            "hash": "",
        }
        block["hash"] = self._compute_hash(block)
        self.chain.append(block)

        logger.info(f"Logged audit block #{new_index} [{event_type}] by {actor_id} on {machine_id}")
        return block

    def verify_chain_integrity(self) -> bool:
        """
        Validates that all blocks in the audit chain are untampered.
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # 1. Check previous hash reference
            if current["previous_hash"] != previous["hash"]:
                logger.error(f"Audit chain broken at block #{i}: previous_hash mismatch!")
                return False

            # 2. Check current block hash
            if current["hash"] != self._compute_hash(current):
                logger.error(f"Audit chain block #{i} has been tampered with!")
                return False

        return True

    def get_history(self, machine_id: str | None = None) -> list[dict[str, Any]]:
        """Retrieves audit trail history with optional machine filtering."""
        if machine_id:
            return [b for b in self.chain if b.get("machine_id") in [machine_id, "GLOBAL"]]
        return self.chain
