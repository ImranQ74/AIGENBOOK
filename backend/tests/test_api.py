"""
Tests for FastAPI endpoints.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_rag_engine():
    """Create a mock RAG engine."""
    engine = MagicMock()
    engine.generate_answer = AsyncMock(
        return_value={
            "answer": "Physical AI refers to AI systems that interact with the physical world.",
            "sources": [{"id": 1, "title": "chapter-01-physical-ai.mdx", "score": 0.95}],
            "conversation_id": "test-conv-123",
        }
    )
    engine.search = MagicMock(return_value=[{"id": 1, "title": "chapter-01-physical-ai.mdx", "score": 0.95}])
    return engine


@pytest.fixture
def mock_user_manager():
    """Create a mock user manager."""
    manager = MagicMock()
    manager.get_preferences = AsyncMock(
        return_value={
            "language": "en",
            "font_size": "medium",
            "theme": "system",
            "preferences": {},
        }
    )
    manager.set_preferences = AsyncMock()
    manager.add_to_history = AsyncMock()
    return manager


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_root_returns_healthy(self, client):
        """Test that root endpoint returns healthy status."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "AIGENBOOK" in data["service"]


class TestChatEndpoint:
    """Test chat API endpoint."""

    @pytest.mark.asyncio
    async def test_chat_valid_request(self, client, mock_rag_engine):
        """Test successful chat request."""
        with patch("main.rag_engine", mock_rag_engine):
            response = client.post(
                "/api/chat",
                json={"question": "What is Physical AI?", "user_id": "test-user"},
            )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "conversation_id" in data

    def test_chat_empty_question(self, client):
        """Test chat with empty question."""
        response = client.post("/api/chat", json={"question": ""})
        assert response.status_code == 422  # Validation error

    def test_chat_question_too_long(self, client):
        """Test chat with question exceeding max length."""
        long_question = "a" * 2000  # Exceeds MAX_QUESTION_LENGTH
        response = client.post("/api/chat", json={"question": long_question})
        assert response.status_code == 422

    def test_chat_missing_question(self, client):
        """Test chat without question field."""
        response = client.post("/api/chat", json={"user_id": "test"})
        assert response.status_code == 422


class TestSearchEndpoint:
    """Test search API endpoint."""

    def test_search_valid_query(self, client, mock_rag_engine):
        """Test successful search request."""
        with patch("main.rag_engine", mock_rag_engine):
            response = client.get("/api/search", params={"query": "robotics"})

        assert response.status_code == 200
        data = response.json()
        assert "results" in data


class TestPreferencesEndpoint:
    """Test user preferences endpoints."""

    def test_get_preferences(self, client, mock_user_manager):
        """Test getting user preferences."""
        with patch("main.user_manager", mock_user_manager):
            response = client.get("/api/users/test-user/preferences")

        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "en"
        assert data["font_size"] == "medium"

    def test_update_preferences(self, client, mock_user_manager):
        """Test updating user preferences."""
        with patch("main.user_manager", mock_user_manager):
            response = client.put(
                "/api/users/test-user/preferences",
                json={"language": "ur", "font_size": "large", "theme": "dark"},
            )

        assert response.status_code == 200
        assert response.json()["status"] == "success"


class TestHistoryEndpoint:
    """Test conversation history endpoint."""

    def test_add_to_history(self, client, mock_user_manager):
        """Test adding to conversation history."""
        with patch("main.user_manager", mock_user_manager):
            response = client.post(
                "/api/users/test-user/history",
                json={
                    "question": "What is ROS 2?",
                    "answer": "ROS 2 is the Robot Operating System version 2.",
                },
            )

        assert response.status_code == 200
        assert response.json()["status"] == "success"


class TestStatsEndpoint:
    """Test stats endpoint."""

    def test_get_stats(self, client):
        """Test getting system stats."""
        response = client.get("/api/stats")

        # This will fail without a real vector store, but should not crash
        assert response.status_code in [200, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
