# 🛡️ Data Governance, Incident Response & Runbooks Log

Production data pipelines inevitably encounter real-world data drift, network anomalies, and platform deprecations. This document serves as an engineering ledger tracking historical pipeline anomalies, Root Cause Analyses (RCA), and the defensive remediation strategies deployed to ensure downstream data warehouse integrity.

---

## 📑 Historical Incident Ledger

### Incident #001: Upstream Schema Anomalies & Duplicate Event Delivery
* **Status:** Resolved ✅
* **Severity:** Medium (Prevented schema corruption/inflation in downstream analytics reporting)
* **Date Discovered:** June 15, 2026

#### 🔍 Root Cause Analysis (RCA)
During automated validation testing iterations utilizing `dbt test`, the data pipeline execution halted upon catching data integrity failures originating from upstream mock-application simulation rules (network retry errors and unauthenticated visitor page interactions):
1. **`not_null` constraint failure on `user_id`**: 8 raw clickstream tracking records returned null/blank strings.
2. **`unique` constraint failure on `event_id`**: 1 duplicate record payload detected within a single micro-batch transmission, emulating network delivery retries.
3. **Inconsistent Categorical Text Casing**: Discovered variant casing on string URI elements (e.g., mixed variations of `/HOME` vs `/home`), threatening future categorical aggregations.

#### 🛠️ Engineering Remediation Strategy
Rather than allowing upstream telemetry anomalies to corrupt core analytical layers, a defensive data transformation layer was engineered natively inside `transform/models/stg_clickstream_events.sql`:
* **Null Handling:** Applied a `COALESCE()` token fallback function to map empty profile identifiers uniformly as `'ANONYMOUS'`.
* **Deduplication:** Implemented an analytical window function utilizing a `QUALIFY ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY timestamp ASC) = 1` constraint to automatically drop redundant network retry duplicates at database runtime.
* **Text Standardization:** Enforced case-folding using the `LOWER()` function across web page paths to ensure strict data quality alignment.

---

### Incident #002: Object Storage Hostname Resolution Error (`Could Not Resolve Hostname`)
* **Status:** Resolved ✅
* **Severity:** High (Halted cloud dbt compilation and completely blocked network connectivity to the data lake)
* **Date Discovered:** June 15 2026

#### 🔍 Root Cause Analysis (RCA)
When migrating the localized dbt pipeline to orchestrate against remote Cloudflare R2 object storage within the GitHub Actions runner, the pipeline repeatedly crashed during database compilation. The network transport layer failed because the target `s3_endpoint` property was compiled with an invalid double protocol prefix: `https://https://[account_id].r2.cloudflarestorage.com`. 

The root cause was an architectural mismatch between configuration layers: the encrypted GitHub Repository Secret vault had the `https://` protocol prefix manually typed inside the vault box, while the `.github/workflows/dbt_run.yml` step was *also* hardcoding a prefix before injecting the environment variable.

#### 🛠️ Engineering Remediation Strategy
* **Configuration Standardization:** Aligned string properties by removing the hardcoded protocol string out of the repository workflow file entirely, relying strictly on clean environment variable tokenization syntax: `s3_endpoint: \"{{ env_var('DBT_R2_ENDPOINT') }}\"`.
* **Infrastructure Lock-In:** Documented the required format for the GitHub repository secret to ensure future rotatable keys strictly maintain a fully qualified URI format without breaking downstream string interpolation blocks.

---

### Incident #003: Cloud Runner Environment Deprecation (Node.js 20 Migration)
* **Status:** Resolved ✅
* **Severity:** Low (Log noise and proactive disruption mitigation)
* **Date Discovered:** June 15 2026

#### 🔍 Root Cause Analysis (RCA)
GitHub issued a platform deprecation warning alerting the repository that core marketplace actions (`actions/checkout@v4` and `actions/setup-python@v5`) were executing on an outdated Node.js 20 runtime environment. With the platform scheduling an immediate hard enforcement cutoff migrating runners to a Node.js 24 environment, outdated dependency tags posed a future compilation maintenance risk.

#### 🛠️ Engineering Remediation Strategy
* **Dependency Upgrades:** Proactively updated the CI/CD workflow build definitions inside `.github/workflows/dbt_run.yml` to track the newest major semantic version tags optimized for the Node.js 24 runtime engine.
* **Refactored Framework:** * Upgraded `actions/checkout@v4` ➡️ `actions/checkout@v5`
  * Upgraded `actions/setup-python@v5` ➡️ `actions/setup-python@v6`
This completely eliminated runner deprecation log noise and insulated the automated orchestration engine against platform breaking changes.

---

### Incident #004: DuckDB Automated Extension Loading Failure
* **Status:** Resolved ✅
* **Severity:** High (Prevented DuckDB database engine from scanning remote cloud object storage files)
* **Date Discovered:** June 15 2026

#### 🔍 Root Cause Analysis (RCA)
During early testing phases, DuckDB threw runtime execution errors when attempting to query remote `s3://` bucket paths. Because DuckDB operates completely in-memory inside a transient, vanilla GitHub Actions Ubuntu virtual container, it lacked the native transport protocols required to read remote, encrypted SSL network file structures over a network interface by default.

#### 🛠️ Engineering Remediation Strategy
* **Profile Configuration Enrichment:** Refactored the dynamic profile generation script in the automation workflow to explicitly declare required database modules during runner startup.
* **Extension Declarations:** Appended the `httpfs` extension array constraint directly into the compiled output target profile:
  ```yaml
  extensions:
    - httpfs
This forces the ephemeral cloud container database instance to instantly fetch and initialize secure network filesystem capabilities before compiling models, establishing a fluid handshake with Cloudflare R2 storage.


## 🔄 The Incident Resolution & Development Runbook

To maintain pipeline stability, all pipeline changes, test failures, or model additions must step through this strict **5-Stage Production Lifecycle Runbook**:
[1. Local Replicated Failure] ➡️ [2. RCA Documentation] ➡️ [3. Defensive SQL Engineering] ➡️ [4. Local Quality Test Gate] ➡️ [5. CI/CD Git Deployment]

1. **Replicate Locally:** If a test fails in production, copy down data files or execute `dbt test --target dev` locally to capture the stack trace.
2. **Log the Incident:** Document the anomaly, root cause, and intended remediation path in this file under a new incident entry.
3. **Apply Defensive Transformation:** Implement cleaning features (`COALESCE`, `LOWER`, window function filters) directly into staging models to ensure errors are handled dynamically at runtime.
4. **Pass Local Quality Gates:** Execute local validation commands. Do not push to remote code hosting if these fail:
```bash
   dbt run --target dev
   dbt test --target dev
```
5. **Deploy via Semantic Commits:** Push verified logic using strict, professional semantic commit phrasing:
```bash
    git add .
    git commit -m "fix: resolve clickstream duplication and missing user profiles via staging deduplication"
    git push origin main
```
