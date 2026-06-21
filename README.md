# 🚀 Automated Data Lakehouse Pipeline (dbt + DuckDB + Cloudflare R2)

A production-grade, serverless data lakehouse architecture designed to ingest, serialize, and transform automated daily micro-batches of user clickstream events. This pipeline enforces strict data quality gates and processes compressed, columnar Apache Parquet payloads into analytical Medallion layers—all operating securely within a $0 cloud infrastructure footprint.

---

## 🏗️ Architecture Overview

The pipeline leverages an in-memory compute model paired with cloud object storage to decouple storage from compute, eliminating fixed server costs entirely.

```text
[Upstream Application]
          ⬇️ (Daily Micro-Batches)
[Python Ingestion (producer.py)] 
          ⬇️ (Snappy-Compressed Parquet Byte Stream)
[Cloudflare Worker Gateway]
          ⬇️ (Dynamic Hive-Style Routing: dt=YYYY-MM-DD/)
[Cloudflare R2 (Partitioned Parquet Lake)]
          ⬇️ (Decoupled Compute Layer via S3 API)
[GitHub Actions Runner (CI/CD)] ➡️ [dbt Core + DuckDB Engine] ➡️ [Data Quality Gates (dbt build)]
          ⬇️
[Staging ➡️ Marts Tables]
```
* **Ingestion Layer (Cloudflare Workers):** A serverless JavaScript runtime gateway that handles incoming POST requests, wraps binary memory arrays into ```Uint8Array``` streams, and safely routes payloads without server overhead.
* **Storage Layer (Cloudflare R2):** A highly cost-effective, zero-egress object storage solution acting as our cold data landing zone, organized using Hive-style partitioning ```(dt=YYYY-MM-DD/)``` to optimize file exploration.
* **Orchestration Layer (GitHub Actions):** A secure CI/CD engine that triggers on branch commits or a daily cron schedule to spin up transient execution environments.
* **Database & Transformation Engine (dbt Core + DuckDB):** An embedded, high-performance analytical database engine that utilizes partition pruning to scan remote R2 paths directly via the HTTP/S3 API, normalizes complex schemas, and handles analytical table modeling.

---

## ⚡ Performance & Storage Optimizations
* **Columnar Serialization (Apache Parquet):** Migrated the upstream Python producer engine from sending bloated JSON text arrays to streaming Snappy-compressed Apache Parquet binary payloads. This drastically reduces network bandwidth, memory consumption, and the cloud storage footprint.
* **Hive-Style Partitioning:** Configured the Cloudflare Worker serverless gateway to automatically organize incoming streams into dynamic date-based directories ```(dt=YYYY-MM-DD/)```.
* **Partition Pruning with DuckDB:** Updated downstream dbt source schemas to leverage DuckDB's native ```read_parquet()``` function. This enables partition pruning, allowing the query engine to completely skip scanning directories outside the target execution dates, optimizing warehouse compute efficiency.


## 🛡️ Data Governance & Incident Response

Real-world web telemetry is prone to data drift, duplication, and schema corruption. To safeguard the integrity of downstream analytics, this architecture implements **defensive staging transformations** and **automated data quality gates**.

Our pipeline enforces:
* **Uniqueness Constraints:** To trap and eliminate at-least-once network retry duplication.
* **Nullability Enforcement:** To catch anonymous tracking blocks and uniformly resolve structural gaps.
* **Schema Validation:** Strict evaluation of accepted categorical strings (e.g., matching verified device profiles).

A complete, transparent ledger documenting historical root cause analyses (RCA) and mitigation paths—including infrastructure variable debugging and automated dependency isolation— is maintained in the **[Incidents & Runbooks Log](./INCIDENTS.md)**.

---

## 📂 Repository Structure

```text
├── .github/workflows/
│   └── dbt_run.yml       # CI/CD orchestration and automated runtime schedule
├── transform/
│   ├── models/
│   │   ├── schema.yml    # Data quality test definitions and column documentation
│   │   ├── staging/      # Silver layer: defensive cleaning & deduplication
│   │   └── marts/        # Gold layer: business intelligence views and analytics
│   └── dbt_project.yml   # dbt configuration metadata
├── src/
│   └── index.js          # Cloudflare Worker gateway routing raw binary to R2
├── wrangler.jsonc        # Infrastructure-as-code binding maps for Cloudflare
├── producer.py           # Ingestion script optimizing and serializing row batches to Parquet
├── requirements.txt      # Consolidated project dependencies pinned for reproducibility
├── INCIDENTS.md          # Production engineering incident logs and runtime runbooks
└── README.md             # Project overview and architectural blueprint
```
---
## ⚙️ Local Development Quickstart
### 1. Prerequisites
* Python 3.13.2
* DuckDB extension capabilities (```httpfs``` required for remote connections)

2. Installation & Setup
Clone the repository and install the verified core dependencies:

### 2. Installation & Setup
Clone the repository and install the verified core dependencies from the root folder:
```bash
pip install -r requirements.txt
```
### 2. Execution Runbook
To manually trigger the localized transformation and testing suite, navigate to the dbt project root and run:
```bash
cd transform
dbt run --target dev
```