# Biodiversity Intelligence AI

AI-powered conversational environmental scientist for biodiversity and ecosystem analysis.

## Features

- Scientific knowledge base with FAO, IPCC and IPBES sources
- ChromaDB vector retrieval / RAG
- Gemini integration
- Soil: pH, organic carbon, moisture
- Land use / land cover
- Biodiversity: species richness, habitat diversity
- Climate: temperature, rainfall
- Human impact: pollution, deforestation
- Text and structured JSON input
- Clarifying questions
- Multi-turn conversation memory
- Multi-metric reasoning
- Evidence-backed recommendations
- Impacted metrics, time horizon and confidence
- Optional coordinates
- Tests, Docker and GitHub Actions

## Architecture

User -> Frontend -> FastAPI -> Parser -> Memory/Clarification
-> ChromaDB/RAG -> Scientific Evidence -> Multi-Metric Reasoning
-> Gemini narrative layer -> Evidence-backed recommendations

Gemini is not the sole source of knowledge. Retrieved scientific evidence and deterministic reasoning form the grounding layer.

## Run

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `.env` from `.env.example` and add your Gemini API key.

Seed ChromaDB:

```powershell
python -m backend.knowledge.seed_chroma
```

Start:

```powershell
uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000

API docs: http://127.0.0.1:8000/docs

## Example input

```json
{
  "soil": {"ph": 6.2, "organic_carbon": 0.3, "moisture": 18},
  "land": {"use": "monoculture wheat", "cover": "low"},
  "biodiversity": {"species_richness": "low", "habitat_diversity": "low"},
  "climate": {"temperature": 31, "rainfall": "low"},
  "human_impact": {"pollution": "low", "deforestation": "medium"},
  "region": "semi-arid",
  "latitude": 15.3,
  "longitude": 75.8
}
```

The system does not invent quantitative improvement percentages. It only reports quantitative claims when matching evidence supports them.
