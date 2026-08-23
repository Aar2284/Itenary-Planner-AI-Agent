# TripPlanner

An AI-powered travel budget assistant that helps travelers plan, allocate, and track their trip expenses in real-time with currency conversion.

## Features

- Smart trip setup with destination, dates, and budget
- Automatic budget allocation across spending categories
- Real-time expense logging with live currency conversion
- Proactive spending alerts and threshold notifications
- Interactive chat interface

## Tech Stack

- **Backend:** Python, Flask, Groq API (LLM)
- **Frontend:** HTML, CSS, JavaScript
- **API Integration:** Frankfurter API (exchange rates)

## Setup

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and add your Groq API key
6. Run: `python app.py`
7. Open http://localhost:5000

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Chat interface |
| `/api/chat` | POST | Send message to agent |
| `/api/status` | GET | Get trip budget status |
| `/api/expenses` | GET | Get expense history |
| `/api/reset` | POST | Reset session |

## Running Tests

```bash
cd agent
pytest tests/ -v