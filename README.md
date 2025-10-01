## Exam Preparation & Study Planning – Prototype

FastAPI + Experta rule engine to generate personalized study timetables. Stateless; exports CSV/PDF. Frontend is a single static HTML page.

### Requirements

- Python 3.10+
- pip

### Install

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install fastapi uvicorn experta pydantic weasyprint reportlab pytest httpx
```

**Note:** If WeasyPrint fails to install on your platform, PDF export will automatically fall back to ReportLab.

### Run API

```bash
uvicorn backend.app.main:app --port 8000
```

The API will be available at `http://127.0.0.1:8000`. Visit `http://127.0.0.1:8000/docs` for interactive API documentation.

### Open Frontend

Open `frontend/index.html` directly in your browser. The frontend will connect to the API at `http://localhost:8000`.

Alternatively, serve the frontend with a static server:
```bash
python -m http.server 5500 --directory frontend
```
Then visit `http://localhost:5500/index.html`.

### API

- POST `/api/generate` → returns JSON with schedule, summaries, explanations
- GET `/api/download/csv` → CSV content
- GET `/api/download/pdf` → base64 PDF

### Tests

```bash
pytest -q
```

### Features

- **Rule-based Expert System**: 50+ rules covering:
  - Urgency (14 rules): Time-to-exam prioritization
  - Mastery (9 rules): Low mastery topics get more time
  - Difficulty (5 rules): Harder topics boosted
  - Importance (9 rules): Course importance weighting
  - Exam Type (4 rules): MCQ, written, practical, oral adjustments
  - Prerequisites (5 rules): Ensure proper sequencing
  - Spaced Repetition (16 rules): Optimize retention
  - Combos (36 rules): Low mastery + high difficulty, importance + difficulty
  - Penalties (2 rules): Reduce high-mastery topic time
  - Triage (4 rules): Handle large topics
  - Buffer (2 rules): Pre-exam review sessions

- **Smart Allocation**:
  - Respects daily caps and weekly availability patterns
  - Honors preferred session lengths (25/50 min)
  - Enforces minimum breaks between sessions
  - Normalizes to available hours with conflict warnings

- **Exports**: CSV and PDF downloads of generated schedules
- **Stateless**: No database required
- **Rule Explanations**: Each session shows which rules fired and why


