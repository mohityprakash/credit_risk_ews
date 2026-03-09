# Credit Risk Early Warning System

AI-powered news intelligence system that ingests near-real-time news, filters credit-relevant events, enriches article risk signals, computes entity trend metrics, and serves both an API and dashboard.

## Why this matters for credit risk
Credit deterioration often appears first in fragmented news flow before formal rating actions or defaults. This system demonstrates a practical **early warning workflow** for:
- monitoring issuers, banks, sovereigns, and sectors,
- surfacing risk categories tied to a transparent taxonomy,
- aggregating article-level signals into entity-level momentum.

## Architecture

```text
            +------------------+
            |  GDELT API       |
            +---------+--------+
                      |
                 /ingest endpoint
                      |
              +-------v--------+
              | Article Store  |  SQLite + SQLAlchemy
              +-------+--------+
                      |
       relevance filter + entity extraction
                      |
               /analyze/pending
                      |
              +-------v--------+
              | Enrichment     |  Rule-based fallback / OpenAI JSON
              +-------+--------+
                      |
              +-------v--------+
              | Trend Engine   |  Risk Momentum Score
              +-------+--------+
                      |
         +------------+------------+
         |                         |
   FastAPI endpoints         Streamlit dashboard
```

## Project structure

```text
credit-risk-ews/
  app/
    api/
    core/
    db/
    ingestion/
    models/
    prompts/
    services/
    ui/
    utils/
  scripts/
  tests/
  data/
  .env.example
  README.md
  requirements.txt
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Run backend (FastAPI)

```bash
uvicorn app.main:app --reload --port 8000
```

## Run dashboard (Streamlit)

```bash
streamlit run app/ui/dashboard.py
```

## Demo mode (no API key required)

```bash
python scripts/seed_demo_data.py
```

This seeds realistic credit-risk articles and analyses so the dashboard and API are immediately demoable.

## API endpoints

- `GET /health`
- `POST /ingest`
- `GET /articles`
- `GET /articles/{id}`
- `GET /entities`
- `GET /entities/{name}/signals`
- `POST /analyze/{id}`
- `POST /analyze/pending`

### Sample calls

```bash
curl -X POST http://localhost:8000/ingest
curl -X POST http://localhost:8000/analyze/pending
curl http://localhost:8000/entities
```

## Config (`.env`)

- `OPENAI_API_KEY`
- `NEWS_PROVIDER`
- `GDELT_QUERY`
- `DATABASE_URL`
- `ENABLE_LLM_ENRICHMENT`
- `INGEST_LOOKBACK_HOURS`
- `MAX_ARTICLES_PER_RUN`
- `OPENAI_MODEL`
- Risk momentum weights

## Risk taxonomy
- Liquidity Risk
- Default Risk
- Downgrade Risk
- Refinancing Risk
- Covenant Risk
- Fraud / Governance Risk
- Regulatory Risk
- Macro / Sovereign Risk
- Counterparty Risk
- Sector Stress

## Explainability design
- Relevance filter logs keyword hits and score.
- LLM output constrained to strict JSON schema with parser + fallback.
- Entity Risk Momentum Score uses weighted, configurable factors.
- Dashboard emphasizes rationale, categories, and trend visibility.

## Screenshots
- _Add dashboard screenshots here._

## How this maps to credit risk early warning systems
- **Signal ingestion layer:** captures news that can lead market repricing or rating changes.
- **Event relevance layer:** narrows to credit-sensitive developments.
- **Analyst assist layer:** generates consistent summaries and risk rationale.
- **Portfolio surveillance layer:** computes entity-level momentum for triage.
- **Governance layer:** explicit taxonomy and transparent scoring support model risk review.

## Interview talking points
- Tradeoff between precision and recall in relevance filtering.
- Why JSON-only enrichment improves reliability in production pipelines.
- How configurable momentum weights support challenger model experiments.
- Failure handling: deduplication, malformed JSON, missing API keys, empty ingestion batches.

## Future improvements
- Add richer NER (spaCy) and ticker resolution.
- Add historical backtesting and alert thresholds.
- Add authentication and role-based API access.
- Containerize with Docker Compose.
- Introduce background scheduler (APScheduler/Celery) for recurring ingestion.
