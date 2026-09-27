# Conversational AI on Synthetic Data

## How to run the code 
`Open docker desktop and run postgres`
`streamlit run app6.py`


## Goal
Build a conversational AI application with two core capabilities:
1. Generate realistic synthetic data from SQL schemas.
2. Query that data with natural language and return clear results.

The end result should feel like a practical "talk to your database" assistant, even when no production data is available.

## Core Capabilities

### 1) Synthetic Data Generation
- Parse SQL schema definitions to extract:
	- Tables
	- Columns and data types
	- Primary/foreign keys
	- Constraints
- Generate realistic data that preserves relational integrity.
- Support configurable row counts per table (for example, 1,000 rows).

### 2) Conversational Querying
- Accept natural language questions about the data.
- Translate questions into SQL safely and reliably.
- Execute queries and return results as:
	- Text summaries
	- Tables
	- Plots/charts where helpful

## Phased Delivery

### Phase 1: Data Generation Engine
- Implement SQL schema parser.
- Build synthetic data generator with constraint awareness.
- Validate generated data for FK and type correctness.

### Phase 2: Conversational Core
- Add NL-to-SQL pipeline with structured outputs.
- Add query validation and execution flow.
- Provide explainable responses (what query ran and why).

### Phase 3: User Experience
- Build interactive UI.
- Add visual result rendering (tables + charts).
- Improve prompts, guardrails, and error handling.

## Technical Stack
- LLM: Gemini 2.0 Flash or newer
	- Use streaming responses where appropriate.
	- Use function calling and structured JSON outputs for reliability.
- SDK: Google GenAI SDK (with Vertex AI authentication via GCP)
- UI: Streamlit or Gradio
- Database: PostgreSQL
- Packaging/Runtime: Docker
- Observability: Langfuse

## Recommended Architecture
1. Schema Ingestion
2. Synthetic Data Service
3. Query Orchestrator (NL -> SQL -> execution)
4. Result Formatter (text/table/chart)
5. UI Layer
6. Observability + Prompt/Query traces

## Minimum Acceptance Criteria
- Can ingest at least one multi-table schema with foreign keys.
- Can generate valid synthetic data for all tables without constraint violations.
- Can answer natural language questions with executable SQL.
- Can display outputs in text and table form, plus at least one chart type.
- Can run locally with Docker.
- Captures key interactions in Langfuse.

## Stretch Goals
- Domain-aware data realism profiles (finance, retail, healthcare, etc.).
- Auto-generated data quality report after synthesis.
- Query feedback loop (detect bad SQL and self-correct).
- Role-based query safety policies.

## Implementation Notes
- Prefer deterministic intermediate formats (structured JSON) between components.
- Keep SQL generation guarded with schema-aware constraints.
- Add lightweight evaluation cases early (for both data quality and query quality).
- Treat observability as a first-class feature, not a final add-on.# conversation-on-syn-data
