# MdEC Starter

Lightweight starter for your MdEC idea.

Structure:
- frontend/  (React + Vite, TypeScript)
- backend/   (FastAPI)

Quick start (frontend):
- cd frontend
- npm install
- npm run dev

Quick start (backend):
- cd backend
- python -m venv .venv
- .\.venv\Scripts\activate
- pip install -r requirements.txt
- uvicorn main:app --reload

This project is isolated and does NOT touch any VAGUS/NIaC or GitOps automation.