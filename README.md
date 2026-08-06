<div align="center">

# 🐍 SnakeSense

### AI-Assisted Snake Species Identification & Snakebite Emergency Guidance for India

**Computer Vision · Retrieval-Augmented Generation · Multilingual Clinical Triage**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-EfficientNet--B0-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-FF6F00?style=for-the-badge)](https://www.trychroma.com/)


</div>

---

> [!IMPORTANT]
> SnakeSense is a **decision-support and educational tool**, not a diagnostic or clinical device. Every prediction and RAG-generated answer is shipped with an explicit non-diagnostic disclaimer at the API level. This project does not replace antivenom administration protocols, hospital triage, or professional medical evaluation.

---

**Output**
<img width="1535" height="864" alt="appui" src="https://github.com/user-attachments/assets/50b2f06f-b67a-41de-bbea-3cea5a8f2c3e" /> <br> <br> 
<img width="1536" height="864" alt="Screenshot 2026-07-28 151101" src="https://github.com/user-attachments/assets/ad21f316-0281-4c10-a108-e869708527f2" /> <br> <br>
<img width="1536" height="863" alt="WhatsApp Image 2026-07-28 at 3 11 17 PM" src="https://github.com/user-attachments/assets/859c1658-d63f-401c-b979-a09a1cfb61cf" /> <br> <br>
<img width="1536" height="864" alt="Screenshot 2026-07-28 142019" src="https://github.com/user-attachments/assets/00e3aec8-ba60-458e-adb3-7b9f5bf65543" /> <br> <br>
<img width="1536" height="864" alt="Screenshot 2026-07-28 142254" src="https://github.com/user-attachments/assets/d2c84190-9180-4a0a-83e5-8c9c8da5832f" /> <br> <br>
<img width="1536" height="864" alt="Screenshot 2026-07-28 142227" src="https://github.com/user-attachments/assets/3fe709dd-1587-46ad-89fc-33fc754bbaf0" /> <br> <br>

---

## Key Features

- **Multimodal Diagnostic Pipeline** — A single Streamlit interface unifies image-based species identification, structured symptom triage, and open-ended conversational Q&A into one clinical workflow rather than three disconnected tools.
- **Confidence-Aware Vision Inference** — The classifier doesn't just return a top prediction; it returns a full top-3 ranked list, computes softmax-calibrated confidence, and explicitly raises a `is_low_confidence` flag below a 40% threshold so ambiguous or blurry images are never silently over-trusted.
- **WHO/NCDC-Aligned Clinical Triage Logic** — A deterministic rules engine maps reported symptoms (ptosis, dyspnea, spontaneous bleeding, local swelling, time elapsed since bite) directly to an urgency tier and a structured `dos` / `donts` action protocol, rather than relying on a language model to reason about emergency medicine live.
- **Grounded RAG Assistant** — Free-text questions are answered by an LLM constrained to a ChromaDB-indexed knowledge base, engineered to reduce hallucination risk on high-stakes queries like "what do I do if bitten by a Common Krait at night."
- **Trilingual by Design** — Species common names and the assistant's language mode are natively surfaced in **English, Hindi (हिंदी), and Gujarati (ગુજરાતી)**, reflecting the real linguistic context of rural snakebite incidents in India.
- **Session-Aware Context Injection** — The chat assistant carries forward the "active species context" from a user's most recent image upload within the same session, so follow-up questions don't require re-stating which snake was identified.
- **Typed, Contract-First API Surface** — Every endpoint (`/predict`, `/triage`, `/chat`, `/health`) is backed by explicit Pydantic response models, giving the system a stable, versionable contract instead of ad-hoc JSON.
- **Lifespan-Managed Model & Index Loading** — The FastAPI `lifespan` context loads the model checkpoint, class mapping, and RAG knowledge base index exactly once at startup rather than per-request, keeping inference latency low and avoiding redundant I/O.

---

## System Architecture & Pipeline

SnakeSense is architected around a single FastAPI application (`app/main.py`) that owns model lifecycle, request validation, and routing, fronted by a Streamlit multi-tab client (`app_ui.py`). The backend loads its EfficientNet-B0 checkpoint and class mapping once at process startup via a `lifespan` context manager, and simultaneously triggers `index_knowledge_base()` to prepare the ChromaDB vector store for the RAG assistant — meaning the first request served is already warm.

Each of the three user-facing capabilities routes to an isolated concern: `/predict` is a pure computer-vision path (image in, ranked species predictions out), `/triage` is a pure deterministic-logic path (symptom JSON in, urgency classification out, **no model inference involved**), and `/chat` is the only path that touches the LLM, and only after retrieval has grounded it in indexed source material.

```mermaid
graph TB
    subgraph Client["Client Layer"]
        UI[Streamlit UI — app_ui.py]
        Tab1["📷 Tab 1: Species ID"]
        Tab2["🚨 Tab 2: Bite Triage"]
        Tab3["💬 Tab 3: Chat Assistant"]
        UI --> Tab1
        UI --> Tab2
        UI --> Tab3
    end

    subgraph API["FastAPI Backend — app/main.py"]
        Health["GET /health"]
        Predict["POST /predict"]
        Triage["POST /triage"]
        Chat["POST /chat"]
        CORS["CORS Middleware<br/>(allow_origins: *)"]
    end

    subgraph Vision["Computer Vision Subsystem"]
        Preprocess["torchvision transforms<br/>Resize 256² → CenterCrop 224²<br/>Normalize (ImageNet stats)"]
        Model["EfficientNet-B0<br/>15-class head"]
        ClassMap["class_mapping.json"]
        SpeciesDB["species_db.py<br/>get_species_info()"]
    end

    subgraph Clinical["Clinical Triage Subsystem"]
        Rules["Deterministic WHO/NCDC<br/>Rules Engine"]
    end

    subgraph RAG["RAG Assistant Subsystem"]
        Retriever["ChromaDB Vector Store"]
        Embedder["Sentence Embeddings"]
        LLM["Orchestrated LLM"]
        KB["Verified Wildlife &<br/>WHO/NCDC Knowledge Base"]
    end

    Tab1 -->|multipart image| Predict
    Tab2 -->|JSON symptoms| Triage
    Tab3 -->|JSON query + context| Chat

    Predict --> CORS --> Preprocess --> Model --> ClassMap --> SpeciesDB --> Predict
    Triage --> CORS --> Rules --> Triage
    Chat --> CORS --> Retriever
    KB --> Embedder --> Retriever
    Retriever -->|retrieved context| LLM --> Chat

    style Client fill:#1a1a2e,stroke:#5B8CFF,color:#fff
    style API fill:#16213e,stroke:#00d9ff,color:#fff
    style Vision fill:#0f3460,stroke:#e94560,color:#fff
    style Clinical fill:#3a0f3a,stroke:#e94560,color:#fff
    style RAG fill:#1b3a2e,stroke:#4ade80,color:#fff
```

### Data Ingestion & Model Pipeline

The vision model's path from raw image to structured prediction follows a fixed preprocessing contract that must match training-time normalization exactly, since any mismatch here silently degrades accuracy without raising an error.

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Streamlit UI
    participant API as FastAPI /predict
    participant T as Preprocessing Pipeline
    participant M as EfficientNet-B0
    participant DB as species_db.py

    U->>UI: Upload snake image (jpg/jpeg/png)
    UI->>API: POST /predict (multipart file)
    API->>API: Validate content_type is image/*
    API->>API: PIL.Image.open().convert("RGB")
    API->>T: Resize (256, 256)
    T->>T: CenterCrop (224, 224)
    T->>T: ToTensor()
    T->>T: Normalize (mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
    T->>M: Forward pass on DEVICE (CUDA/CPU)
    M->>M: torch.softmax(outputs, dim=1)
    M->>M: torch.topk(probabilities, k=3)
    M->>DB: get_species_info(scientific_name) for each of top-3
    DB-->>M: common_name, local_names, toxicity_status, venom_type, is_big_four
    M->>API: Ranked SpeciesPrediction[] + confidence scores
    API->>API: Flag is_low_confidence if top confidence < 40%
    API-->>UI: PredictionResponse (JSON)
    UI-->>U: Ranked predictions + safety disclaimer
```

> [!NOTE]
> The `/triage` endpoint is intentionally excluded from any model or LLM call path. Emergency urgency classification is computed by deterministic conditional logic in `main.py` alone — a design choice made so that clinical urgency decisions are auditable, reproducible, and not subject to model drift or hallucination.

---

## Tech Stack Matrix

| Category | Technology | Purpose |
|---|---|---|
| **Computer Vision / Core AI** | PyTorch, `torchvision.models.efficientnet_b0` | Backbone architecture for 15-class snake species image classification |
| **Computer Vision / Core AI** | OpenCV | Image preprocessing utilities in the training/data pipeline |
| **RAG** | ChromaDB | Vector store for indexing and retrieving the verified wildlife/medical knowledge base |
| **RAG** | Hugging Face (Sentence-Transformers ecosystem) | Text embedding generation for semantic retrieval |
| **Backend & API** | FastAPI | Typed REST API serving `/health`, `/predict`, `/triage`, and `/chat` |
| **Backend & API** | Pydantic | Request/response schema validation (`PredictionResponse`, `TriageRequest`, `ChatResponse`, etc.) |
| **Backend & API** | Python `contextlib.asynccontextmanager` (FastAPI `lifespan`) | One-time model checkpoint, class mapping, and RAG index loading at startup |
| **Frontend / UI** | Streamlit | Multi-tab client for image upload, symptom triage form, and chat interface |
| **Frontend / UI** | Pillow (PIL) | Client and server-side image handling |
| **Infrastructure** | CORS Middleware (FastAPI) | Cross-origin access enabled for local testing and prospective mobile client connectivity |
| **Data & Experimentation** | Jupyter Notebooks (`snakesense.ipynb`, `preprocessing.ipynb`, `data_augmentation.ipynb`, `dataset_loader.ipynb`, `duplicate_detection.ipynb`) | Dataset engineering, preprocessing, augmentation, deduplication, and model training workflows |
| **Testing** | Pytest (`conftest.py`, `tests/`) | Test suite for API endpoint correctness |

---

### Logged Performance Metrics

| Metric | Value | Notes |
|---|---|---|
| **Backbone** | EfficientNet-B0 | `torchvision.models.efficientnet_b0`, custom 15-class head |
| **Top-3 Test Accuracy** | **87.24%** | Formally logged during test-set evaluation |
| **Inference Latency** | **< 100 ms / image** | Measured on GPU/CUDA |
| **Classes Registered** | **15 species** | Indices `0`–`14`, sourced from `class_mapping.json` |
| **Per-Species Precision / Recall** | *Not logged* | Not recorded in the training run logs — flagged here rather than estimated |
| **Confusion Matrix** | *Not logged* | Full per-class confusion matrix was not captured during this training run |

---

## Directory Structure

```SNAKESENSE/
├── .gitignore
├── README.md
├── app_ui.py
├── conftest.py
├── data_augmentation.ipynb
├── dataset_loader.ipynb
├── duplicate_detection.ipynb
├── preprocessing.ipynb
├── snakesense.ipynb
├── app/
│   ├── main.py
│   ├── rag_engine.py
│   ├── schemas.py
│   ├── species_db.py
├── checkpoints/
├── chroma_db/
│   ├── chroma.sqlite3
├── data/
│   ├── knowledge_base/
│   │   ├── indian_species_profiles.txt
│   │   └── who_ncdc_guidelines.txt
│   ├── Processed_Images/
│   │   ├── Processed_test/
│   │   ├── Processed_train/
│   │   └── Processed_valid/
│   └── raw/
│       ├── test/
│       ├── train/
│       ├── valid/
│       └── README.dataset.txt
├── models/
└── tests/
    ├── test_api.py

```

> [!NOTE]
> `checkpoints/` and `models/` are referenced explicitly by path in `app/main.py`'s `lifespan` handler but are excluded from version control via `.gitignore` (standard practice for binary model artifacts) — they must be generated locally by running the training notebooks or downloaded separately before the API will start.

---

## Getting Started & Setup Guide

### Prerequisites

- **Python**: 3.10 or higher
- **CUDA-capable GPU** (recommended): for sub-100ms inference latency; the app auto-detects and falls back to CPU otherwise (`torch.device("cuda" if torch.cuda.is_available() else "cpu")`)
- **Core dependencies**: PyTorch, torchvision, FastAPI, Uvicorn, Streamlit, Pillow, ChromaDB, Pydantic, Pytest


### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/Samirhadiyal/SnakeSense.git
cd SnakeSense

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install torch torchvision fastapi uvicorn streamlit pillow chromadb pydantic pytest

# 5. Start the FastAPI backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 6. In a separate terminal, start the Streamlit UI
streamlit run app_ui.py
```

The Streamlit UI expects the backend at `http://127.0.0.1:8000` by default (hardcoded `API_URL` in `app_ui.py`) — update this constant if deploying the backend elsewhere.

### Running Tests

```bash
pytest tests/ -v
```

---

## API & Usage Reference

### Endpoint Summary

| Method | Endpoint | Payload | Description |
|---|---|---|---|
| `GET` | `/health` | — | Returns service status, active device (CPU/CUDA), model load state, and registered class count |
| `POST` | `/predict` | `multipart/form-data` (image file) | Runs EfficientNet-B0 inference, returns top-3 ranked species predictions with confidence, toxicity, and localized names |
| `POST` | `/triage` | `application/json` (symptom fields) | Deterministic WHO/NCDC-aligned urgency classification with action protocol |
| `POST` | `/chat` | `application/json` (query, context, language) | RAG-grounded conversational answer from the verified knowledge base |

### `GET /health`

**Sample Response**

```json
{
  "status": "healthy",
  "device": "cuda",
  "model_loaded": true,
  "classes_registered": 15
}
```

### `POST /predict`

**Request**: `multipart/form-data` with a single `file` field (`image/jpeg`, `image/png`, or `image/jpg`).

**Sample Response**

```json
{
  "status": "success",
  "is_low_confidence": false,
  "top_predictions": [
    {
      "rank": 1,
      "scientific_name": "Naja naja",
      "common_name": "Indian Cobra",
      "local_names": {
        "en": "Indian Cobra",
        "hi": "नाग",
        "gu": "નાગ"
      },
      "confidence_percentage": 92.47,
      "toxicity_status": "HIGHLY VENOMOUS",
      "venom_type": "Neurotoxic",
      "is_big_four": true
    },
    {
      "rank": 2,
      "scientific_name": "Ptyas mucosa",
      "common_name": "Indian Rat Snake",
      "local_names": {
        "en": "Indian Rat Snake",
        "hi": "धामन",
        "gu": "ધામણ"
      },
      "confidence_percentage": 5.12,
      "toxicity_status": "NON-VENOMOUS",
      "venom_type": "None",
      "is_big_four": false
    },
    {
      "rank": 3,
      "scientific_name": "Bungarus caeruleus",
      "common_name": "Common Krait",
      "local_names": {
        "en": "Common Krait",
        "hi": "करैत",
        "gu": "કરૈત"
      },
      "confidence_percentage": 1.83,
      "toxicity_status": "HIGHLY VENOMOUS",
      "venom_type": "Neurotoxic",
      "is_big_four": true
    }
  ],
  "safety_disclaimer": "CRITICAL DISCLAIMER: AI image predictions are non-diagnostic. Never handle wild snakes or delay medical evaluation based on prediction confidence."
}
```

> [!NOTE]
> The exact `local_names`, `toxicity_status`, and `venom_type` values shown above illustrate the response *shape* as defined by `SpeciesPrediction` in `app/schemas.py` and populated via `species_db.get_species_info()`; the specific per-species metadata values live in that module and are not reproduced here verbatim from source.

### `POST /triage`

**Sample Request**

```json
{
  "bitten": true,
  "time_elapsed_minutes": 15,
  "local_swelling": true,
  "drooping_eyelids": true,
  "difficulty_breathing": false,
  "spontaneous_bleeding": false
}
```

**Sample Response**

```json
{
  "urgency_level": "CRITICAL",
  "suspected_toxicity": "Systemic Envenoming (Neurotoxic / Haemotoxic)",
  "action_protocol": {
    "immediate_action": "RUSH TO NEAREST DISTRICT HOSPITAL OR PRIMARY HEALTH CENTER",
    "dos": [
      "Reassure the victim and keep them completely calm.",
      "Immobilize the bitten limb with a splint or loose bandage.",
      "Remove tight jewelry, rings, watches, or restrictive clothing.",
      "Transport the victim to a facility with Antivenom (ASV) and ICU facilities immediately."
    ],
    "donts": [
      "DO NOT cut or incision the bite wound.",
      "DO NOT attempt to suck venom by mouth or device.",
      "DO NOT apply a tight tourniquet or tight rope.",
      "DO NOT apply herbal remedies, ice, or chemicals.",
      "DO NOT give the victim alcohol, caffeine, or pain medication."
    ]
  },
  "emergency_contacts": ["108 (Emergency Ambulance)", "112 (National Emergency Response)"]
}
```

### `POST /chat`

**Sample Request**

```json
{
  "query": "What should I do if someone is bitten by a Common Krait at night?",
  "species_context": "Predicted species: Bungarus caeruleus (Common Krait)",
  "language": "English"
}
```

**Sample Response**

```json
{
  "query": "What should I do if someone is bitten by a Common Krait at night?",
  "answer": "Common Krait bites are frequently painless and may go unnoticed until neurotoxic symptoms appear. Seek emergency care immediately regardless of visible symptoms, immobilize the limb, and monitor closely for drooping eyelids or breathing difficulty en route to the nearest facility with antivenom availability.",
  "language": "English"
}
```

> [!NOTE]
> The `answer` field above is an illustrative example of the response shape, not a verbatim transcript of `rag_engine.generate_rag_answer()` output — actual answers are generated dynamically from the indexed knowledge base at query time.







---

<div align="center">

**⚠️ SnakeSense is a decision-support tool, not a substitute for professional medical care. In a suspected snakebite emergency, seek immediate hospital treatment.**

</div>
