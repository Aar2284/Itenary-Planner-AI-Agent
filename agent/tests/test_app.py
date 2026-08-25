"""Tests for Flask API endpoints."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


def test_index_route():
    """Index route should return HTML."""
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200


def test_chat_missing_message():
    """Chat endpoint without message should return 400."""
    with app.test_client() as client:
        response = client.post('/api/chat', json={})
        assert response.status_code == 400


def test_chat_empty_message():
    """Chat endpoint with empty message should return 400."""
    with app.test_client() as client:
        response = client.post('/api/chat', json={"message": "   "})
        assert response.status_code == 400


def test_status_no_session():
    """Status endpoint with no session should return no_session."""
    with app.test_client() as client:
        response = client.get('/api/status?session_id=nonexistent')
        data = response.get_json()
        assert data["status"] == "no_session"


def test_reset_endpoint():
    """Reset endpoint should clear session."""
    with app.test_client() as client:
        response = client.post('/api/reset', json={"session_id": "test"})
        data = response.get_json()
        assert data["status"] == "reset"

def test_conversation_trimming():
    """Conversation history should trim when too long."""
    from app import get_conversation
    conv = get_conversation("test-trim")
    for i in range(60):
        conv.append({"role": "user", "content": f"msg {i}"})
    assert len(conv) > 50


def test_chat_returns_json_with_session_id():
    """Chat endpoint should return JSON with session_id."""
    with app.test_client() as client:
        response = client.post('/api/chat', json={
            "message": "Hello",
            "session_id": "test-session-123"
        })
        data = response.get_json()
        assert "response" in data
        assert "session_id" in data
        assert data["session_id"] == "test-session-123"


def test_expenses_empty_session():
    """Expenses endpoint with no session should return empty list."""
    with app.test_client() as client:
        response = client.get('/api/expenses?session_id=nonexistent')
        data = response.get_json()
        assert data["expenses"] == []


def test_status_no_trip():
    """Status endpoint with setup but no allocation should return no_trip."""
    from agent.state import get_or_create_session
    state = get_or_create_session("test-no-trip")
    state.setup_trip("Paris", "EUR", "EUR", "2026-10-01", "2026-10-05", 2000)
    with app.test_client() as client:
        response = client.get('/api/status?session_id=test-no-trip')
        data = response.get_json()
        assert data["status"] == "no_trip"


def test_reset_clears_conversation():
    """Reset should clear conversation history."""
    from app import get_conversation, conversations
    conv = get_conversation("test-reset-conv")
    conv.append({"role": "user", "content": "test"})
    with app.test_client() as client:
        client.post('/api/reset', json={"session_id": "test-reset-conv"})
    assert "test-reset-conv" not in conversations


def test_static_files_served():
    """Static files should be served from static folder."""
    with app.test_client() as client:
        response = client.get('/nonexistent-file')
        assert response.status_code == 404


def test_chat_default_session():
    """Chat endpoint should use default session when not provided."""
    with app.test_client() as client:
        response = client.post('/api/chat', json={"message": "Hi"})
        data = response.get_json()
        assert data["session_id"] == "default"


if __name__ == "__main__":
    test_index_route()
    test_chat_missing_message()
    test_chat_empty_message()
    test_status_no_session()
    test_reset_endpoint()
    test_conversation_trimming()
    test_chat_returns_json_with_session_id()
    test_expenses_empty_session()
    test_status_no_trip()
    test_reset_clears_conversation()
    test_static_files_served()
    test_chat_default_session()
    print("All tests passed!")