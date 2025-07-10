# Medical AI Assistant (SWARM of Agents)

This repository implements a **multi-agent AI system** designed to assist medical professionals with diagnostic workflows, image analysis, patient data retrieval, and automatic report generation. Built around a Strands-style orchestration of specialized agents, the project demonstrates end-to-end integration of machine learning, natural language, and web technologies.

---

## 🚀 Project Overview

The platform orchestrates a collection of autonomous agents that collaborate to:

1. **Classify MRI images** for tumor likelihood using a DenseNet-121 based neural network.
2. **Segment detected tumors** with a U‑Net model to delineate affected regions.
3. **Retrieve patient history** and context through a Retrieval‑Augmented Generation (RAG) agent backed by ChromaDB.
4. **Perform clinical triage**, estimating urgency based on image analysis and retrieved data.
5. **Generate structured reports** in PDF format summarizing the entire workflow.
6. **Validate the produced reports** before finalization.

A lightweight React frontend provides a user interface for clinicians, while a FastAPI backend powers the agent infrastructure and exposes REST endpoints.

---

## 🗂️ Repository Structure

```
/
├── backend/                 # FastAPI server and agent implementation
│   ├── Dockerfile
│   ├── main.py              # entry point for local/production use
│   ├── requirements.txt
│   └── src/
│       ├── agents/          # individual agent classes (classification, segmentation, etc.)
│       ├── config/          # settings and prompt templates
│       └── tools/           # utility modules (image processing, RAG, PDF generation)
├── frontend/                # React + Vite UI
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── components/      # React components (sidebar, workflow, reports)
│       ├── assets/          # static assets and helper scripts
│       └── context/         # React context for global state
├── docker-compose.yml       # orchestrates backend + frontend containers
└── swarm_strands.ipynb      # notebook with experiments and agent examples
```

---

## 💻 Technologies Used

| Layer       | Technologies                            |
|-------------|-----------------------------------------|
| Backend     | Python 3.11, FastAPI, Strands Agents   |
| Database    | ChromaDB (SQLite)                      |
| ML Models   | OpenAI API, DenseNet‑121, U‑Net        |
| Frontend    | React 18, Vite                         |
| Container   | Docker, Docker Compose                 |

---

## 🔧 Prerequisites

- Docker Engine & Docker Compose
- Git (for cloning the repo)
- An OpenAI API key (stored in environment variables)

---

## 🛠️ Setup and Running

1. **Clone the repository**

   ```bash
   git clone https://github.com/your_username/your_repo.git
   cd your_repo
   ```

2. **Environment configuration**

   Create a `.env` file inside the `backend/` directory containing:
   ```env
   OPENAI_API_KEY=your_api_key_here
   OTHER_OPTIONAL_SETTINGS=...
   ```

3. **Build and start services**

   ```bash
   docker-compose up -d --build
   ```

4. **Access the system**

   - Frontend UI:  `http://localhost:3000`
   - Backend API docs (Swagger):  `http://localhost:8000/docs`

---

## 🧠 Workflow Summary

1. A clinician uploads MRI scans via the frontend.
2. The backend invokes the **classification agent** to evaluate tumour probability.
3. If positive, the **segmentation agent** processes the images.
4. The **RAG agent** fetches relevant patient documents from the embedded ChromaDB corpus.
5. **Orchestrator and planner agents** coordinate the above steps and trigger the **triage agent**.
6. Once all sub‑tasks complete, the **report agent** generates a consolidated PDF.
7. The **validator agent** checks consistency before the report is delivered to the user.

---

## 📁 Important Files

- `backend/src/agents/*.py` – implementations of each agent
- `backend/src/tools/` – shared utilities (image and file handling)
- `frontend/src/components/` – React components forming the UI
- `docker-compose.yml` – container definitions
- `swarm_strands.ipynb` – exploratory notebook showcasing agent interactions

---

## 📦 Customization and Development

- Add new agents under `backend/src/agents` following the existing base‑class pattern.
- Update prompts in `backend/src/config/prompts.py` for model behavior tuning.
- Use the notebook to experiment with agent sequences and dataset ingestion.

---

## 📄 License & Attribution

[Specify license here, e.g. MIT] — please replace this section with your project’s license details.

---

> ⚠️ **Note:** This is an experimental project intended for research and internal use. Medical applications should undergo rigorous validation before deployment.
