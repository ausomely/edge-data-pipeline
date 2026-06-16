# 🚀 Automated Data Lakehouse Pipeline (dbt + DuckDB + Cloudflare R2)

A production-grade, serverless data lakehouse architecture designed to ingest, clean, and transform automated daily micro-batches of user clickstream events. This pipeline enforces strict data quality gates and processes raw, nested JSON payloads into analytical Medallion layers—all operating securely within a $0 cloud infrastructure footprint.

---

## 🏗️ Architecture Overview

The pipeline leverages an in-memory compute model paired with cloud object storage to decouple storage from compute, eliminating fixed server costs entirely.

[Upstream Application]
⬇️ (Daily Micro-Batches)
[Python Ingestion (producer.py)]
⬇️ (Secure API Gateway)
[Cloudflare R2 (Raw JSON Lake)]
⬇️ (Decoupled Compute Layer)
[GitHub Actions Runner (CI/CD)] ➡️ [dbt Core + DuckDB Engine] ➡️ [Data Quality Gates (dbt test)]
⬇️
[Staging ➡️ Marts Tables]

* **Storage Layer (Cloudflare R2):** A highly cost-effective, zero-egress object storage solution acting as our cold data landing zone.
* **Orchestration Layer (GitHub Actions):** A secure CI/CD engine that triggers on branch commits or a daily cron schedule to spin up transient execution environments.
* **Database & Transformation Engine (dbt Core + DuckDB):** An embedded, high-performance analytical database engine that scans remote R2 paths directly, normalizes variants, and handles analytical table modeling.

---

## 🛡️ Data Governance & Incident Response

Real-world web telemetry is prone to data drift, duplication, and schema corruption. To safeguard the integrity of downstream analytics, this architecture implements **defensive staging transformations** and **automated data quality gates**.

Our pipeline enforces:
* **Uniqueness Constraints:** To trap and eliminate at-least-once network retry duplication.
* **Nullability Enforcement:** To catch anonymous tracking blocks and uniformly resolve structural gaps.
* **Schema Validation:** Strict evaluation of accepted categorical strings (e.g., matching verified device profiles).

A complete, transparent ledger documenting historical root cause analyses (RCA) and mitigation paths is maintained in the **[Incidents & Runbooks Log](./INCIDENTS.md)**.

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
├── producer.py           # Ingestion script simulating messy real-world tracking arrays
├── INCIDENTS.md          # Production engineering incident logs and runtime runbooks
└── README.md             # Project overview and architectural blueprint
```
---
## ⚙️ Local Development Quickstart
### 1. Prerequisites
* Python 3.13.2
* DuckDB extension capabilities (httpfs required for remote connections)

2. Installation & Setup
Clone the repository and install the verified core dependencies:

### 2. Installation & Setup
Clone the repository and install the verified core dependencies:
```bash
pip install -r requirements.txt
pip install dbt-duckdb
```
### 2. Execution Runbook
To manually trigger the localized transformation and testing suite, navigate to the dbt project root and run:
```bash
cd transform
dbt run --target dev
dbt test --target dev
```