# Snippet-Sage
A modern solution to storing, searching, and sharing your favorite code snippets

Built with **Python (FastAPI)** backend and a **Next.js (React)** web frontend

## Current State
- **Python backend** (backend/) - FastAPI server exposing snippet database
- **Python Package** (backend/snippet_sage/) - CLI and database layer (add, list, search, delete snippets)
- **Next.js Frontend** (frontend/snippet-sage-web/) - a full React application connecting to the API
- **Working Features:**
  - CLI Snippet Management
  - Backend REST API (/api/snippets)
  - Fronted snippet list (fetched from API)

## Roadmap
|   Features   |   Status   |
|--------------|------------|
| CLI Snippet Management | Done |
| REST API | Done |
| Frontend Snippet List | Done |
| Search/Filter Snippets | Next |
| Create/Delete from Frontend | Planned |
| User Authentication | Planned |
| AI Suggestions | Planned |
| Dark Mode & UI Revamp | Planned |
| Share snippets via link | Future |

## Getting Started
### Prerequisites:
- Python 3.10+ & pip
- Node.js 18+ & npm
- A modern browser

### 1. Backend (Python and FastAPI)
```
cd backend
pip install -r requirements.txt # or: pip install fastapi uvicorn
uvicorn server:app --reload
```
API runs at **http://localhost:8000**.

Test it: ``` curl http://localhost:8000/api/snippets ```

### 2. Frontend (Next.js)
```
cd frontend/snippet-sage-web
npm install
npm run dev
```
Open **http://localhost:3000** in your browser – you should see the snippet list from your database.

### 3. CLI (Direct Usage)
```
cd backend
python -m snippet_sage --help
```
**Examples:**
```
python -m snippet_sage add --title "Hello" --code "print('hello')" --language python
python -m snippet_sage list
```
