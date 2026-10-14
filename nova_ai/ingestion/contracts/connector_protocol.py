# ─────────────────────────────────────────────────────────────────────────────
# Nova AI · showcase excerpt
# Source: nova_ai/ingestion/contracts/connector_protocol.py (private repository)
# Complete module, unchanged.
# © Apex Intelligence. Shown for demonstration only; all rights reserved.
# ─────────────────────────────────────────────────────────────────────────────

"""
Formal protocol contract for Nova AI ingestion connectors.
"""

from __future__ import annotations

from typing import Any, AsyncIterator, Protocol, runtime_checkable

from nova_ai.connectors.types import ConnectorResult
from nova_ai.ingestion.contracts.record_batch import RecordBatch
from nova_ai.ingestion.contracts.sync_state import SyncState


@runtime_checkable
class ConnectorProtocol(Protocol):
    """
    Structural protocol for connectors used by the batch ingestion runner.

    A connector does not need to inherit from a specific base class as long as it
    provides these methods with compatible behavior.
    """

    async def test_connection(self) -> ConnectorResult:
        """Return connector health without writing application data."""
        ...

    async def extract_batches(
        self,
        object_name: str,
        sync_state: SyncState | None = None,
        options: dict[str, Any] | None = None,
    ) -> AsyncIterator[RecordBatch]:
        """Yield bounded raw record batches for ingestion."""
        ...
