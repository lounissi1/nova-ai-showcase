# Ingestion benchmark

High-scale CSV ingestion through the staging `COPY` path, measured locally on synthetic revenue
data (one machine, local PostgreSQL), 2026-07-01.

| Rows | Runtime | Rows per second | Rejected | Canonical rows written |
|---:|---:|---:|---:|---:|
| 100,000 | 12.6 s | 7,960 | 0 | 100,000 |
| 500,000 | 27.8 s | 18,009 | 0 | 500,000 |
| **1,000,000** | **58.5 s** | **17,098** | 0 | 1,000,000 |

Target for this phase: 1 million rows in 60 seconds or less, without skipping validation,
deduplication or metric building. **Passed.**

## What made it fast

The first implementation wrote batches with many small `DELETE` and `UPSERT` statements. The
optimised path:

1. Streams validated records into a staging table with PostgreSQL `COPY`.
2. Runs set-based validation and deduplication in SQL.
3. Promotes the batch to canonical records in one bulk statement.

At 1M rows this is roughly an **80× reduction in write operations**.

## Limits stated honestly

- Synthetic data and a single local machine; cloud numbers will differ.
- Python-side transformation (hashing and normalisation per row) is now the main cost; going far
  beyond this needs multiprocessing or moving more work into the database.
