"""
Pytest configuration and fixtures.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def anyio_backend():
    """Set the async backend for pytest-asyncio."""
    return "asyncio"


@pytest.fixture
def mock_rag_engine():
    """Create a mock RAG engine for testing."""
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
    """Create a mock user manager for testing."""
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


@pytest.fixture
def mock_vector_store():
    """Create a mock vector store for testing."""
    store = MagicMock()
    store.search = MagicMock(return_value=[])
    store.add_documents = MagicMock()
    store.get_collection_stats = MagicMock(return_value={"points_count": 100, "collections": ["aigenbook_chunks"]})
    return store


@pytest.fixture
def client(mock_rag_engine, mock_user_manager):
    """Create a test client with mocked dependencies."""
    from fastapi.testclient import TestClient

    # Override the global instances
    import main
    from main import app

    main.rag_engine = mock_rag_engine
    main.user_manager = mock_user_manager
    return TestClient(app)
