# AI Startup Pitch Validator

> Submit your startup pitch and get brutally honest, investor-lens feedback — scored across traction, market size, differentiation, team, and business model.


---

## Overview

Most startup pitch feedback is generic ("needs more market research") or comes too late (after you've already pitched). AI Startup Pitch Validator simulates an experienced investor's evaluation of your pitch across the dimensions that actually matter in early-stage funding decisions.

Input your pitch as free text or structured fields, and get a scored breakdown with specific, actionable feedback per dimension — not just a vague summary.

---

## Features

- **Multi-dimensional scoring** — evaluates across 6 investor criteria with individual scores (0–10)
- **Investor persona simulation** — AI adopts a VC lens: skeptical, pattern-matching, focused on scalability
- **Strength / weakness breakdown** — explicit list of what's working and what would get you passed on
- **One-liner generator** — produces a crisp elevator pitch from your input
- **Red flag detection** — surfaces statements that would make investors uncomfortable
- **Follow-up questions** — the questions an investor would ask you in the room

---

## Evaluation Dimensions

| Dimension | What's Assessed |
|-----------|----------------|
| Problem Clarity | Is the problem real, specific, and painful? |
| Market Size | TAM/SAM/SOM — is this a venture-scale opportunity? |
| Differentiation | What makes this defensible vs. alternatives? |
| Business Model | Is the monetization logical and scalable? |
| Traction | Any evidence of demand, users, or revenue? |
| Team Signal | Does the pitch convey founder-market fit? |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite + Tailwind CSS |
| Backend | FastAPI (Python) |
| AI | Groq API — Llama 3.3 70B |
| Deployment | Vercel (frontend) + Render (backend) |

---

## Architecture

```
User submits pitch text
        ↓
Frontend → POST /validate (FastAPI)
        ↓
Groq LLM → score each dimension + generate feedback
        ↓
Structured JSON → Frontend renders scorecard + feedback
```

---

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### Environment Variables

**Backend `.env`:**
```
GROQ_API_KEY=your_groq_api_key
```

**Frontend `.env`:**
```
VITE_API_URL=http://localhost:8000
```

---

## API

### `POST /validate`

**Request:**
```json
{
  "pitch": "We're building a B2B SaaS platform that helps..."
}
```

**Response:**
```json
{
  "overall_score": 6.4,
  "one_liner": "A concise version of your pitch in one sentence.",
  "scores": {
    "problem_clarity": 8,
    "market_size": 5,
    "differentiation": 6,
    "business_model": 7,
    "traction": 4,
    "team_signal": 8
  },
  "strengths": ["Clear problem statement", "Strong founder-market fit signals"],
  "weaknesses": ["Market size claim unsupported", "No mention of existing traction"],
  "red_flags": ["'We have no competition' — investors distrust this"],
  "investor_questions": ["What's your CAC and LTV assumption?", "Who else is working on this?"]
}
```

---

## Project Structure

```
ai-startup-pitch-validator/
├── backend/
│   ├── main.py
│   ├── routers/
│   │   └── validate.py
│   ├── services/
│   │   └── ai.py
│   └── requirements.txt
└── frontend/
    └── src/
        ├── App.jsx
        └── components/
            ├── PitchInput.jsx
            ├── ScoreCard.jsx
            ├── FeedbackPanel.jsx
            └── RedFlags.jsx
```

---

