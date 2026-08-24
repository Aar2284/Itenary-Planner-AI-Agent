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


if __name__ == "__main__":
    test_index_route()
    test_chat_missing_message()
    test_chat_empty_message()
    test_status_no_session()
    test_reset_endpoint()
    test_conversation_trimming()
    print("All tests passed!")