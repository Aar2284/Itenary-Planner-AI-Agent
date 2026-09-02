# 🌍 Itenary Budget Planner AI Agent

> **AI-powered travel budget assistant that helps travelers plan, allocate, and track trip expenses in real-time with live currency conversion.**

---

## 🎯 What It Does

TripBudgetBuddy is a conversational AI agent that helps you manage your travel budget through natural language chat. Just tell it your destination, dates, and budget — it handles the rest.

**Example conversation:**

```
USER: "I'm going to Bangkok for 7 days with ₹50,000"

AGENT: Trip set up! Here's a suggested allocation:
       🏨 Lodging:   ₹15,000  (30%)
       🍽️ Food:      ₹10,000  (20%)
       🚕 Transport:  ₹8,000  (16%)
       🎭 Activities: ₹10,000 (20%)
       🛍️ Shopping:   ₹7,000  (14%)

USER: "Spent ฿500 on lunch"

AGENT: Logged! ₹120 deducted from food budget.
       ⚠️ Food is 45% spent but only 14% of trip remains.
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 💬 **Natural Chat** | Talk to the agent like a travel buddy |
| 💱 **Live Rates** | Real-time currency conversion via Frankfurter API |
| 📊 **Budget Tracking** | Visual budget status with category breakdowns |
| 🚨 **Smart Alerts** | Proactive warnings when spending gets risky |
| 🔄 **Multi-Trip** | Manage multiple trips in separate sessions |
| 📱 **Responsive** | Works on desktop and mobile |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.12, Flask |
| **AI Engine** | Groq API (Llama 3.3 70B) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Exchange Rates** | Frankfurter API |
| **State Management** | In-memory session store |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Groq API key ([Get one here](https://console.groq.com))

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/Itenary-Planner-AI-Agent.git
cd Itenary-Planner-AI-Agent

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up environment variables
copy .env.example .env
# Edit .env and add your GROQ_API_KEY

# 6. Run the application
python app.py
```

### Access

Open your browser and navigate to: **http://localhost:5000**

---

## 📁 Project Structure

```
Itenary-Budget-Planner-AI-Agent/
├── agent/
│   ├── prompts.py          # System prompt & tool schemas
│   ├── state.py            # Trip state management
│   ├── tools.py            # Tool dispatcher & handlers
│   └── tests/
│       ├── test_state.py   # State management tests
│       ├── test_tools.py   # Tool dispatcher tests
│       ├── test_prompts.py # Prompt validation tests
│       ├── test_app.py     # API endpoint tests
│       └── README.md       # Test documentation
├── frontend/
│   ├── index.html          # Chat interface
│   ├── style.css           # Dark theme styles
│   └── script.js           # Multi-trip session manager
├── app.py                  # Flask server & agent loop
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | `GET` | Serve chat interface |
| `/api/chat` | `POST` | Send message to agent |
| `/api/status` | `GET` | Get trip budget status |
| `/api/expenses` | `GET` | Get expense history |
| `/api/reset` | `POST` | Reset session |

### Example Request

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I need help planning a trip to Tokyo", "session_id": "my-trip"}'
```

---

## 🧪 Testing

```bash
# Run all tests
cd agent
pytest tests/ -v

# Run specific test file
pytest tests/test_state.py -v

# Run with coverage
pytest tests/ --cov=agent --cov-report=html
```

**Test Coverage:** 45 tests across 4 test files

| File | Tests | Coverage |
|------|-------|----------|
| `test_state.py` | 21 | State management |
| `test_app.py` | 12 | API endpoints |
| `test_prompts.py` | 9 | Prompt validation |
| `test_tools.py` | 8 | Tool dispatcher |

---

## 🎨 How It Works

### Agent Architecture

```
Frontend (Chat UI)
       │
       ▼
Flask API (Orchestrator)
       │
       ▼
Groq LLM (Reasoning)
       │
       ▼
Tool Calls ──▶ State Management
             ──▶ Frankfurter API
             ──▶ Expense Logging
```

### Tool Calling Flow

1. **User sends message** → Flask receives via `/api/chat`
2. **LLM reasons** → Decides which tools to call
3. **Tools execute** → State updates, API calls made
4. **Results fed back** → LLM processes tool outputs
5. **Response generated** → Final text returned to user

---

## 🔐 Environment Variables

| Variable | Description | Required |
|----------|-------------|:--------:|
| `GROQ_API_KEY` | Your Groq API key | ✅ |

---

## 📄 License

This project is for educational purposes.

---

*Built with ❤️ for travelers who want to stay on budget*
