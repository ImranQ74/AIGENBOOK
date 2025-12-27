"""
User management with Neon PostgreSQL integration.
Stores user preferences and conversation history.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, Column, DateTime, String, Text, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Conversation(Base):
    """SQLAlchemy model for conversation history."""

    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserPreferences(Base):
    """SQLAlchemy model for user preferences."""

    __tablename__ = "user_preferences"

    user_id = Column(String(255), primary_key=True)
    language = Column(String(10), default="en")
    font_size = Column(String(20), default="medium")
    theme = Column(String(20), default="system")
    preferences = Column(JSON, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserManager:
    """
    Manages user data with Neon PostgreSQL.
    Falls back to in-memory storage if database is unavailable.
    """

    def __init__(
        self,
        database_url: Optional[str] = None,
    ):
        self.database_url = database_url
        self.use_database = database_url is not None
        self.async_engine = None
        self.async_session = None

        if self.use_database:
            # Create async engine for Neon
            try:
                async_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
                self.async_engine = create_async_engine(
                    async_url,
                    echo=False,
                    pool_size=5,
                    max_overflow=10,
                )
                self.async_session = sessionmaker(self.async_engine, class_=AsyncSession, expire_on_commit=False)
                print("UserManager: Async database engine initialized")
            except Exception as e:
                print(f"UserManager: Failed to create async engine: {e}")
                self.use_database = False
                self._init_memory_fallback()
        else:
            self._init_memory_fallback()

    def _init_memory_fallback(self):
        """Initialize in-memory fallback storage."""
        self._memory_conversations: List[Dict] = []
        self._memory_preferences: Dict[str, Dict] = {}
        print("UserManager: Using in-memory fallback")

    async def close(self):
        """Close database connections."""
        if self.async_engine:
            await self.async_engine.dispose()

    async def _ensure_tables(self):
        """Ensure tables exist (create if needed)."""
        if self.use_database and self.async_engine:
            from sqlalchemy import text

            async with self.async_engine.begin() as conn:
                # Create tables using raw SQL for compatibility
                await conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS conversations (
                        id VARCHAR(36) PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        sources JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )
                await conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        user_id VARCHAR(255) PRIMARY KEY,
                        language VARCHAR(10) DEFAULT 'en',
                        font_size VARCHAR(20) DEFAULT 'medium',
                        theme VARCHAR(20) DEFAULT 'system',
                        preferences JSONB,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )
                # Create indexes
                await conn.execute(
                    text(
                        """
                    CREATE INDEX IF NOT EXISTS idx_conversations_user_id
                    ON conversations(user_id)
                """
                    )
                )

    # ============= Conversation Management =============

    async def add_to_history(
        self,
        user_id: str,
        question: str,
        answer: str,
        sources: Optional[List[Dict]] = None,
        conversation_id: Optional[str] = None,
    ):
        """Add a conversation to history."""
        conv_id = conversation_id or self._generate_id()
        created_at = datetime.utcnow()

        if self.use_database and self.async_session:
            async with self.async_session() as session:
                conv = Conversation(
                    id=conv_id,
                    user_id=user_id,
                    question=question,
                    answer=answer,
                    sources=json.dumps(sources) if sources else None,
                    created_at=created_at,
                )
                session.add(conv)
                await session.commit()
        else:
            self._memory_conversations.append(
                {
                    "id": conv_id,
                    "user_id": user_id,
                    "question": question,
                    "answer": answer,
                    "sources": sources,
                    "created_at": created_at.isoformat(),
                }
            )

    async def get_history(
        self,
        user_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get conversation history for a user."""
        if self.use_database and self.async_session:
            async with self.async_session() as session:
                result = await session.execute(
                    select(Conversation)
                    .where(Conversation.user_id == user_id)
                    .order_by(Conversation.created_at.desc())
                    .limit(limit)
                )
                rows = result.scalars().all()
                return [
                    {
                        "id": row.id,
                        "question": row.question,
                        "answer": row.answer,
                        "sources": json.loads(row.sources) if row.sources else None,
                        "created_at": (row.created_at.isoformat() if row.created_at else None),
                    }
                    for row in rows
                ]
        else:
            return [conv for conv in self._memory_conversations if conv["user_id"] == user_id][:limit]

    # ============= Preferences Management =============

    async def get_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences."""
        if self.use_database and self.async_session:
            try:
                from sqlalchemy import text

                async with self.async_session() as session:
                    result = await session.execute(
                        text("SELECT * FROM user_preferences WHERE user_id = :user_id"),
                        {"user_id": user_id},
                    )
                    row = result.fetchone()
                    if row:
                        return {
                            "language": row.language,
                            "font_size": row.font_size,
                            "theme": row.theme,
                            "preferences": row.preferences,
                        }
            except Exception as e:
                print(f"Error getting preferences: {e}")

        # Default preferences
        return {
            "language": "en",
            "font_size": "medium",
            "theme": "system",
            "preferences": {},
        }

    async def set_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Set user preferences."""
        if self.use_database and self.async_session:
            try:
                from sqlalchemy import text

                async with self.async_session() as session:
                    await session.execute(
                        text(
                            """
                            INSERT INTO user_preferences (user_id, language, font_size, theme, preferences, updated_at)
                            VALUES (:user_id, :language, :font_size, :theme, :preferences, NOW())
                            ON CONFLICT (user_id) DO UPDATE SET
                                language = EXCLUDED.language,
                                font_size = EXCLUDED.font_size,
                                theme = EXCLUDED.theme,
                                preferences = EXCLUDED.preferences,
                                updated_at = NOW()
                        """
                        ),
                        {
                            "user_id": user_id,
                            "language": preferences.get("language", "en"),
                            "font_size": preferences.get("font_size", "medium"),
                            "theme": preferences.get("theme", "system"),
                            "preferences": json.dumps(preferences.get("preferences", {})),
                        },
                    )
                    await session.commit()
            except Exception as e:
                print(f"Error setting preferences: {e}")
        else:
            self._memory_preferences[user_id] = preferences

    # ============= Helper Methods =============

    def _generate_id(self) -> str:
        """Generate a unique ID."""
        import uuid

        return str(uuid.uuid4())
