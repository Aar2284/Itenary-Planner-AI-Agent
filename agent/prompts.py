"""
System Prompt & Tool Schemas
Defines the agent's personality, rules, and tool schemas.
"""

SYSTEM_PROMPT = """You are TripBudgetBuddy - a smart, friendly AI travel budget assistant.

## Your Capabilities
You help travelers:
1. Set up a trip with destination, dates, currencies, and total budget
2. Allocate budget across categories (lodging, food, transport, activities, shopping)
3. Log expenses in local currency - you always convert using live exchange rates
4. Track spending and provide detailed budget status
5. Alert proactively when spending patterns suggest overspending risk

## Core Rules (NEVER break these)
- ALWAYS call get_exchange_rate before logging any expense
- ALWAYS call get_budget_status after logging an expense to check for threshold alerts
- If the status contains alerts, you MUST relay them to the user with context and suggestions
- Never make up exchange rates, budget amounts, or expense data
- All monetary calculations must use tool results, never mental math

## Conversation Flow
1. New user? -> Greet warmly, ask about their trip
2. Trip set up? -> Suggest a budget allocation
3. Budget allocated? -> Ready to log expenses
4. Ongoing? -> Log expenses, provide spending insights

## Personality
- Friendly but financially savvy
- Use relevant emojis sparingly
- Give specific, actionable advice
- Celebrate good budget discipline
"""

# ── Tool Schemas for Groq Function Calling ───────────────────────────

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "setup_trip",
            "description": "Initialize a new trip with destination, dates, currencies, and total budget.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string", "description": "Trip destination, e.g. 'Bangkok, Thailand'"},
                    "home_currency": {"type": "string", "description": "Home currency code, e.g. 'INR'"},
                    "local_currency": {"type": "string", "description": "Local currency code, e.g. 'THB'"},
                    "start_date": {"type": "string", "description": "Start date YYYY-MM-DD"},
                    "end_date": {"type": "string", "description": "End date YYYY-MM-DD"},
                    "total_budget": {"type": "number", "description": "Total budget in home currency"}
                },
                "required": ["destination", "home_currency", "local_currency", "start_date", "end_date", "total_budget"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "allocate_budget",
            "description": "Split total budget across spending categories.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lodging": {"type": "number", "description": "Budget for accommodation"},
                    "food": {"type": "number", "description": "Budget for meals"},
                    "transport": {"type": "number", "description": "Budget for local transport"},
                    "activities": {"type": "number", "description": "Budget for tours and attractions"},
                    "shopping": {"type": "number", "description": "Budget for shopping"}
                },
                "required": ["lodging", "food", "transport", "activities", "shopping"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "Get live exchange rate between two currencies. Must be called before logging expense.",
            "parameters": {
                "type": "object",
                "properties": {
                    "base_currency": {"type": "string", "description": "Source currency, e.g. 'THB'"},
                    "target_currency": {"type": "string", "description": "Target currency, e.g. 'INR'"}
                },
                "required": ["base_currency", "target_currency"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "log_expense",
            "description": "Record an expense in local currency with conversion.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "enum": ["lodging", "food", "transport", "activities", "shopping"]},
                    "amount_local": {"type": "number", "description": "Amount in local currency"},
                    "exchange_rate": {"type": "number", "description": "Rate from get_exchange_rate"},
                    "note": {"type": "string", "description": "Description of expense"}
                },
                "required": ["category", "amount_local", "exchange_rate"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_budget_status",
            "description": "Get complete budget status with spending and alerts.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]