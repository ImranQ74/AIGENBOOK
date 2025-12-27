"""
FastAPI backend for AIGENBOOK RAG Chatbot.
Provides free-tier friendly RAG with Qdrant + local embeddings.
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Optional rate limiting
try:
    from slowapi import Limiter, rate_limit_exceeded_handler
    from slowapi.util import get_remote_address

    SLOWAPI_AVAILABLE = True
except ImportError:
    SLOWAPI_AVAILABLE = False
    logger.warning("slowapi not available, rate limiting disabled")

from config import settings
from document_processor import DocumentProcessor
from rag_engine import RAGEngine
from user_manager import UserManager
from vector_store import VectorStore

# Initialize components
doc_processor = None
vector_store = None
rag_engine = None
user_manager = None

# Rate limiter
if SLOWAPI_AVAILABLE:
    limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
else:
    limiter = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting AIGENBOOK RAG Chatbot...")
    yield
    # Shutdown
    logger.info("Shutting down AIGENBOOK RAG Chatbot...")
    if user_manager:
        await user_manager.close()
    if vector_store:
        vector_store.close()


app = FastAPI(
    title="AIGENBOOK RAG Chatbot API",
    description="Free-tier RAG chatbot for Physical AI textbook",
    version="1.0.0",
    lifespan=lifespan,
)

# Add rate limiter
if SLOWAPI_AVAILABLE:
    app.state.limiter = limiter
    app.add_exception_handler(429, rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============= Pydantic Models =============
# Maximum question length to prevent abuse
MAX_QUESTION_LENGTH = 1000
MAX_USER_ID_LENGTH = 255


class ChatRequest(BaseModel):
    question: str
    user_id: Optional[str] = "anonymous"
    conversation_id: Optional[str] = None
    selected_text: Optional[str] = None

    @field_validator("question")
    @classmethod
    def validate_question(cls, v):
        if not v or not v.strip():
            raise ValueError("Question cannot be empty")
        if len(v) > MAX_QUESTION_LENGTH:
            raise ValueError(f"Question too long (max {MAX_QUESTION_LENGTH} characters)")
        return v.strip()

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v):
        if v and len(v) > MAX_USER_ID_LENGTH:
            raise ValueError(f"User ID too long (max {MAX_USER_ID_LENGTH} characters)")
        return v


class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]
    conversation_id: str


class UserPreferences(BaseModel):
    language: str = "en"
    font_size: str = "medium"
    theme: str = "system"

    @field_validator("language")
    @classmethod
    def validate_language(cls, v):
        if v not in ["en", "ur"]:
            raise ValueError("Language must be 'en' or 'ur'")
        return v

    @field_validator("font_size")
    @classmethod
    def validate_font_size(cls, v):
        if v not in ["small", "medium", "large"]:
            raise ValueError("Font size must be 'small', 'medium', or 'large'")
        return v

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, v):
        if v not in ["light", "dark", "system"]:
            raise ValueError("Theme must be 'light', 'dark', or 'system'")
        return v


class DocumentRequest(BaseModel):
    file_path: str
    chunk_size: Optional[int] = settings.chunk_size
    chunk_overlap: Optional[int] = settings.chunk_overlap

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, v):
        if not v or not v.strip():
            raise ValueError("File path cannot be empty")
        return v


# ============= Lifecycle Events =============


@app.on_event("startup")
async def startup():
    global doc_processor, vector_store, rag_engine, user_manager

    # Initialize vector store
    vector_store = VectorStore(
        collection_name=settings.qdrant_collection_name,
        qdrant_url=settings.qdrant_url,
        qdrant_api_key=settings.qdrant_api_key,
    )

    # Initialize document processor
    doc_processor = DocumentProcessor(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    # Initialize RAG engine
    rag_engine = RAGEngine(
        vector_store=vector_store,
        embedding_model=settings.embedding_model,
        device=settings.embedding_device,
        llm_provider=settings.llm_provider,
        llm_model=settings.llm_model,
        llm_api_base=settings.llm_api_base,
        llm_api_key=settings.llm_api_key,
        top_k=settings.top_k,
    )

    # Initialize user manager (Neon)
    user_manager = UserManager(
        database_url=settings.neon_database_url,
    )

    # Index documents from the textbook
    await index_textbook_documents()

    logger.info("AIGENBOOK RAG Chatbot initialized successfully")


# ============= API Endpoints =============


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AIGENBOOK RAG Chatbot",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """
    Detailed health check endpoint for deployment monitoring.
    Returns status of all components.
    """
    import socket

    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "hostname": socket.gethostname(),
        "components": {},
    }

    # Check vector store
    try:
        if vector_store:
            stats = vector_store.get_collection_stats(settings.qdrant_collection_name)
            health_status["components"]["vector_store"] = {
                "status": "healthy",
                "documents": stats.get("points_count", 0),
            }
        else:
            health_status["components"]["vector_store"] = {"status": "not_initialized"}
    except Exception as e:
        health_status["components"]["vector_store"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        health_status["status"] = "degraded"

    # Check LLM provider
    health_status["components"]["llm"] = {
        "status": "healthy",
        "provider": settings.llm_provider,
        "model": settings.llm_model,
    }

    # Check user manager
    health_status["components"]["database"] = {
        "status": "healthy" if user_manager else "not_initialized",
        "type": "neon" if settings.neon_database_url else "memory",
    }

    return health_status


@app.get("/ready")
async def readiness_check():
    """
    Readiness probe for Kubernetes/railway.
    Returns 200 only when the service is ready to receive traffic.
    """
    try:
        # Check if vector store is ready
        if vector_store:
            vector_store.get_collection_stats(settings.qdrant_collection_name)

        return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=503, detail=f"Service not ready: {e}")


@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit("30/minute") if limiter else lambda x: x
async def chat(request: Request, chat_request: ChatRequest):
    """
    Main chat endpoint - answers questions using RAG from textbook content.
    Rate limited to 30 requests per minute.
    """
    logger.info(f"Chat request from user: {chat_request.user_id}")

    try:
        # Combine selected text with question if provided
        full_question = chat_request.question
        if chat_request.selected_text:
            full_question = f"{chat_request.selected_text}\n\nQuestion: {chat_request.question}"

        # Generate response using RAG
        result = await rag_engine.generate_answer(
            question=full_question,
            user_id=chat_request.user_id or "anonymous",
        )

        logger.info(f"Chat response generated for conversation: {result.get('conversation_id')}")

        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            conversation_id=result.get("conversation_id", ""),
        )

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while generating the response. Please try again.",
        )


@app.get("/api/search")
async def search(query: str, top_k: int = 5):
    """
    Search textbook content without generating an answer.
    """
    try:
        results = await rag_engine.search(query, k=top_k)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/index-document")
async def index_document(request: DocumentRequest, background_tasks: BackgroundTasks):
    """
    Index a new document into the vector store.
    """
    try:
        # Check if file exists
        file_path = Path(request.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Process and index
        chunks = doc_processor.process_file(str(file_path))

        # Add to vector store
        vector_store.add_documents(
            documents=chunks,
            collection_name=settings.qdrant_collection_name,
        )

        return {"status": "success", "chunks_indexed": len(chunks)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats():
    """
    Get statistics about the indexed documents.
    """
    try:
        stats = vector_store.get_collection_stats(settings.qdrant_collection_name)
        return {
            "vector_store": stats,
            "settings": {
                "embedding_model": settings.embedding_model,
                "chunk_size": settings.chunk_size,
                "top_k": settings.top_k,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= User Preferences =============


@app.get("/api/users/{user_id}/preferences")
async def get_preferences(user_id: str):
    """Get user preferences."""
    try:
        prefs = await user_manager.get_preferences(user_id)
        return prefs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/users/{user_id}/preferences")
async def update_preferences(user_id: str, preferences: UserPreferences):
    """Update user preferences."""
    try:
        await user_manager.set_preferences(user_id, preferences.dict())
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/users/{user_id}/history")
async def add_to_history(user_id: str, data: dict):
    """Add conversation to user history."""
    try:
        await user_manager.add_to_history(
            user_id,
            data.get("question", ""),
            data.get("answer", ""),
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= Helper Functions =============


async def index_textbook_documents():
    """Index all markdown files from the docs directory."""
    docs_path = Path(__file__).parent.parent / "docs"

    if not docs_path.exists():
        print(f"Docs directory not found: {docs_path}")
        return

    # Find all markdown files
    md_files = list(docs_path.glob("**/*.md*"))
    print(f"Found {len(md_files)} markdown files to index")

    all_chunks = []

    for md_file in md_files:
        try:
            chunks = doc_processor.process_file(str(md_file))
            all_chunks.extend(chunks)
            print(f"Processed: {md_file.name} ({len(chunks)} chunks)")
        except Exception as e:
            print(f"Error processing {md_file}: {e}")

    if all_chunks:
        # Add to vector store in batches
        batch_size = 100
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i : i + batch_size]
            vector_store.add_documents(
                documents=batch,
                collection_name=settings.qdrant_collection_name,
            )

        print(f"Indexed {len(all_chunks)} document chunks")
    else:
        print("No documents to index")


# ============= Run Server =============

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
