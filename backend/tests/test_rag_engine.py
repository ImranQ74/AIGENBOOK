"""
Tests for RAG engine module.
"""

import sys
from pathlib import Path

import pytest

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class MockSearchResult:
    """Mock search result for testing."""

    def __init__(self, content, source, score=0.9, metadata=None):
        self.content = content
        self.source = source
        self.score = score
        self.metadata = metadata or {}


class MockVectorStore:
    """Mock vector store for testing."""

    def __init__(self):
        self.search_results = []

    def search(self, query, k=5, score_threshold=0.0):
        return self.search_results[:k]


class TestRAGEngine:
    """Test cases for RAGEngine class."""

    def test_build_context(self):
        """Test context building from search results."""
        # Import after setting up path
        from rag_engine import RAGEngine

        mock_store = MockVectorStore()
        mock_store.search_results = [
            MockSearchResult(
                content="Physical AI involves embodied AI systems.",
                source="chapter-01-physical-ai.mdx",
                score=0.95,
            ),
            MockSearchResult(
                content="Humanoid robots have human-like form.",
                source="chapter-02-humanoid-robotics.mdx",
                score=0.85,
            ),
        ]

        # Create engine with mock store (won't actually load models)
        engine = RAGEngine(
            vector_store=mock_store,
            llm_provider="openai",
            llm_model="gpt-3.5-turbo",
        )

        context = engine._build_context(mock_store.search_results)

        assert "Physical AI involves embodied AI systems" in context
        assert "chapter-01-physical-ai.mdx" in context
        assert "Humanoid robots have human-like form" in context
        assert "chapter-02-humanoid-robotics.mdx" in context

    def test_build_prompt(self):
        """Test prompt building for LLM."""
        from rag_engine import RAGEngine

        mock_store = MockVectorStore()
        engine = RAGEngine(
            vector_store=mock_store,
            llm_provider="openai",
            llm_model="gpt-3.5-turbo",
        )

        context = "Test context about robotics."
        question = "What is Physical AI?"

        prompt = engine._build_prompt(question, context)

        assert "Physical AI" in prompt
        assert "Test context about robotics" in prompt
        assert "Answer:" in prompt
        assert "instructions" in prompt.lower()

    def test_format_sources(self):
        """Test source formatting for response."""
        from rag_engine import RAGEngine

        mock_store = MockVectorStore()
        engine = RAGEngine(
            vector_store=mock_store,
            llm_provider="openai",
            llm_model="gpt-3.5-turbo",
        )

        results = [
            MockSearchResult(
                content="Full content here",
                source="chapter-01-physical-ai.mdx",
                score=0.95,
                metadata={"page": 1},
            ),
        ]

        sources = engine._format_sources(results)

        assert len(sources) == 1
        assert sources[0]["title"] == "chapter-01-physical-ai.mdx"
        assert sources[0]["score"] == 0.95
        assert "Full content here" in sources[0]["content_preview"]
        assert sources[0]["id"] == 1

    def test_clean_answer(self):
        """Test answer cleaning."""
        from rag_engine import RAGEngine

        mock_store = MockVectorStore()
        engine = RAGEngine(
            vector_store=mock_store,
            llm_provider="openai",
            llm_model="gpt-3.5-turbo",
        )

        # Test removing artifacts
        dirty_answer = """This is the answer.

```python
def example():
    pass
```

Context: This should be removed
Question: What is this?"""

        cleaned = engine._clean_answer(dirty_answer)

        assert "```python" not in cleaned
        assert "Context:" not in cleaned
        assert "This is the answer" in cleaned

    def test_clean_answer_truncation(self):
        """Test answer truncation at cutoff markers."""
        from rag_engine import RAGEngine

        mock_store = MockVectorStore()
        engine = RAGEngine(
            vector_store=mock_store,
            llm_provider="openai",
            llm_model="gpt-3.5-turbo",
        )

        answer_with_cutoff = """Physical AI is important for robotics.

Question: What is the answer?"""

        cleaned = engine._clean_answer(answer_with_cutoff)

        assert "Physical AI is important for robotics" in cleaned
        assert "Question:" not in cleaned


class TestChatRequest:
    """Test cases for chat request validation."""

    def test_chat_request_creation(self):
        """Test creating a valid chat request."""
        from main import ChatRequest

        request = ChatRequest(question="What is ROS 2?")
        assert request.question == "What is ROS 2?"
        assert request.user_id == "anonymous"
        assert request.conversation_id is None
        assert request.selected_text is None

    def test_chat_request_with_all_fields(self):
        """Test creating a chat request with all fields."""
        from main import ChatRequest

        request = ChatRequest(
            question="Explain bipedal locomotion",
            user_id="user123",
            conversation_id="conv456",
            selected_text="ZMP is a key concept",
        )

        assert request.question == "Explain bipedal locomotion"
        assert request.user_id == "user123"
        assert request.conversation_id == "conv456"
        assert request.selected_text == "ZMP is a key concept"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
