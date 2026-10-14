# ─────────────────────────────────────────────────────────────────────────────
# Nova AI · showcase excerpt
# Source: nova_ai/ingestion/high_scale/copy_loader.py (private repository)
# Excerpt: the bulk COPY path behind the 1M-rows-in-under-a-minute benchmark.
# © Apex Intelligence. Shown for demonstration only; all rights reserved.
# ─────────────────────────────────────────────────────────────────────────────

"""Bulk-load validated revenue records into a staging table with PostgreSQL COPY."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


DEFAULT_STAGING_TABLE = "ingestion_revenue_staging_rows"
STAGING_COPY_FEATURE_FLAG = "NOVA_ENABLE_STAGING_COPY_INGESTION"
TRUE_VALUES = {"1", "true", "yes", "y", "on"}

COPY_COLUMNS: tuple[str, ...] = (
    "staging_batch_id",
    "row_number",
    "raw_record_hash",
    "record_hash",
    "order_id",
    "order_date",
    "customer_id",
    "product_id",
    "product_name",
    "category",
    "region",
    "channel",
    "currency",
    "quantity",
    "unit_price",
    "gross_revenue",
    "cost",
    "source_record",
    "validation_status",
    "validation_errors",
)

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class StagingCopyResult:
    table_name: str
    schema_name: str | None
    rows_copied: int
    columns: tuple[str, ...]


def is_staging_copy_enabled(env: Mapping[str, str] | None = None) -> bool:
    values = os.environ if env is None else env
    return values.get(STAGING_COPY_FEATURE_FLAG, "").strip().lower() in TRUE_VALUES


def quote_identifier(identifier: str) -> str:
    if not _IDENTIFIER_RE.fullmatch(identifier):
        raise ValueError(f"Unsafe SQL identifier: {identifier!r}")

    return f'"{identifier}"'


def build_copy_sql(
    table_name: str = DEFAULT_STAGING_TABLE,
    *,
    columns: Sequence[str] = COPY_COLUMNS,
    schema_name: str | None = None,
) -> str:
    qualified_table = quote_identifier(table_name)

    if schema_name:
        qualified_table = f"{quote_identifier(schema_name)}.{qualified_table}"

    quoted_columns = ", ".join(quote_identifier(column) for column in columns)
    return f"COPY {qualified_table} ({quoted_columns}) FROM STDIN WITH (FORMAT CSV)"

# ... value normalisation and iter_revenue_copy_rows() omitted ...


class AsyncpgStagingCopyLoader:
    async def copy_revenue_records(
        self,
        connection: Any,
        records: Iterable[Mapping[str, Any]],
        *,
        staging_batch_id: str,
        table_name: str = DEFAULT_STAGING_TABLE,
        schema_name: str | None = None,
        start_row_number: int = 1,
        include_source_record: bool = True,
    ) -> StagingCopyResult:
        rows = tuple(
            iter_revenue_copy_rows(
                records,
                staging_batch_id=staging_batch_id,
                start_row_number=start_row_number,
                include_source_record=include_source_record,
            )
        )

        if rows:
            await connection.copy_records_to_table(
                table_name,
                records=rows,
                columns=COPY_COLUMNS,
                schema_name=schema_name,
            )

        return StagingCopyResult(
            table_name=table_name,
            schema_name=schema_name,
            rows_copied=len(rows),
            columns=COPY_COLUMNS,
        )
