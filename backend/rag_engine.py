"""
RAG (Retrieval-Augmented Generation) engine.
Handles question answering using retrieved context.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from sentence_transformers import SentenceTransformer

from vector_store import VectorStore, SearchResult

# Configure logging
logger = logging.getLogger(__name__)

# Optional imports - only needed for local inference
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Optional imports - for API-based inference
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


@dataclass
class AnswerResult:
    """Result from RAG generation."""
    answer: str
    sources: List[Dict[str, Any]]
    retrieved_contexts: List[SearchResult]
    conversation_id: str


class RAGEngine:
    """
    RAG engine for generating answers from textbook content.
    Supports both local transformers models and OpenAI-compatible APIs.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_model: str = "all-MiniLM-L6-v2",
        device: str = "cpu",
        llm_provider: str = "openai",  # Default to API
        llm_model: str = "gpt-3.5-turbo",
        llm_api_base: Optional[str] = None,
        llm_api_key: Optional[str] = None,
        top_k: int = 5,
        similarity_threshold: float = 0.5,
    ):
        self.vector_store = vector_store
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold

        # Reranker (optional)
        self.reranker = None

        # LLM configuration
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.llm_api_base = llm_api_base or os.getenv("LLM_API_BASE")
        self.llm_api_key = llm_api_key or os.getenv("LLM_API_KEY")

        # Initialize LLM
        self._init_llm(device)

    def _init_llm(self, device: str):
        """Initialize the language model based on provider."""
        if self.llm_provider == "openai":
            self._init_openai()
        elif self.llm_provider == "transformers":
            self._init_transformers(device)
        else:
            logger.warning(f"Unknown LLM provider: {self.llm_provider}, defaulting to OpenAI")
            self._init_openai()

    def _init_openai(self):
        """Initialize OpenAI-compatible client."""
        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI package not available, falling back to transformers")
            self.llm_provider = "transformers"
            self._init_transformers("cpu")
            return

        if not self.llm_api_base:
            logger.warning("No LLM_API_BASE set, using default OpenAI endpoint")
            self.llm_api_base = "https://api.openai.com/v1"

        if not self.llm_api_key:
            logger.warning("No LLM_API_KEY set - API calls may fail")

        try:
            self.openai_client = OpenAI(
                base_url=self.llm_api_base,
                api_key=self.llm_api_key or "dummy-key",
            )
            logger.info(f"OpenAI client initialized for {self.llm_api_base}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    def _init_transformers(self, device: str):
        """Initialize local Transformers model."""
        if not TRANSFORMERS_AVAILABLE:
            logger.error("Transformers package not available")
            raise ImportError("transformers package required for local inference")

        logger.info(f"Loading local LLM: {self.llm_model} on {device}")

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.llm_model)

            # Use quantization for CPU efficiency
            if device == "cpu":
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.llm_model,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True,
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.llm_model,
                    torch_dtype=torch.float16,
                    device_map="auto",
                )

            # Create generation pipeline
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
            )
            logger.info("Local LLM loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load local LLM: {e}")
            raise

    async def generate_answer(
        self,
        question: str,
        user_id: str = "anonymous",
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate an answer to a question using RAG.

        Args:
            question: User's question
            user_id: User identifier
            conversation_id: Optional conversation ID for continuity

        Returns:
            Dictionary with answer, sources, and conversation_id
        """
        import uuid
        if not conversation_id:
            conversation_id = str(uuid.uuid4())[:8]

        try:
            # Step 1: Retrieve relevant documents
            retrieved = self.vector_store.search(
                query=question,
                k=self.top_k,
                score_threshold=self.similarity_threshold,
            )

            # Step 2: Rerank if available
            if self.reranker and len(retrieved) > 2:
                retrieved = self._rerank(question, retrieved[:10])[:5]
            else:
                retrieved = retrieved[: self.top_k]

            # Step 3: Build context from retrieved documents
            context = self._build_context(retrieved)

            # Step 4: Generate answer
            prompt = self._build_prompt(question, context)
            answer = await self._generate(prompt)

            # Step 5: Format sources
            sources = self._format_sources(retrieved)

            return {
                "answer": answer,
                "sources": sources,
                "conversation_id": conversation_id,
            }
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise

    async def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for documents without generating an answer.
        """
        results = self.vector_store.search(query, k=k)
        return self._format_sources(results)

    def _rerank(
        self, query: str, candidates: List[SearchResult]
    ) -> List[SearchResult]:
        """Rerank retrieved documents using cross-encoder."""
        if not self.reranker:
            return candidates

        # Score each candidate
        pairs = [(query, c.content) for c in candidates]
        scores = self.reranker(pairs)

        # Sort by score
        scored = list(zip(candidates, scores))
        scored.sort(key=lambda x: x[1], reverse=True)

        return [c for c, _ in scored]

    def _build_context(self, retrieved: List[SearchResult]) -> str:
        """Build context string from retrieved documents."""
        contexts = []

        for i, result in enumerate(retrieved):
            # Format with source citation
            source_name = os.path.basename(result.source)
            context = f"[Source {i + 1}: {source_name}]\n{result.content}"
            contexts.append(context)

        return "\n\n".join(contexts)

    def _build_prompt(self, question: str, context: str) -> str:
        """
        Build the prompt for the LLM.
        """
        prompt = f"""You are a helpful AI teaching assistant for a Physical AI and Humanoid Robotics textbook.

Based on the following context from the textbook, please answer the user's question.

Context:
{context}

Question: {question}

Instructions:
1. Answer based ONLY on the provided context
2. If the answer is not in the context, say "I don't have enough information to answer this question based on the textbook."
3. Keep your answer concise and clear
4. Use your general knowledge to explain concepts, but cite the textbook when appropriate

Answer:"""

        return prompt

    async def _generate(self, prompt: str) -> str:
        """Generate text using the configured LLM."""
        if self.llm_provider == "openai":
            return await self._generate_with_openai(prompt)
        else:
            return await self._generate_with_transformers(prompt)

    async def _generate_with_openai(self, prompt: str) -> str:
        """Generate using OpenAI-compatible API."""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI teaching assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=512,
                temperature=0.7,
            )

            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def _generate_with_transformers(self, prompt: str) -> str:
        """Generate using HuggingFace Transformers."""
        import torch

        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt")

        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                inputs["input_ids"],
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        # Decode
        full_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract just the answer (after "Answer:")
        if "Answer:" in full_output:
            answer = full_output.split("Answer:")[-1].strip()
        else:
            answer = full_output[len(prompt):].strip()

        # Clean up
        answer = self._clean_answer(answer)

        return answer

    def _clean_answer(self, answer: str) -> str:
        """Clean up generated answer."""
        # Remove any continued generation artifacts
        lines = answer.split("\n")
        cleaned_lines = []

        for line in lines:
            # Skip if line looks like a command or artifact
            if line.strip().startswith("```") or "Context:" in line:
                continue
            cleaned_lines.append(line)

        answer = "\n".join(cleaned_lines)

        # Truncate at obvious cutoffs
        cutoff_markers = ["\n\nQuestion:", "\n\nContext:", "\n\nSource ["]
        for marker in cutoff_markers:
            if marker in answer:
                answer = answer.split(marker)[0]

        return answer.strip()

    def _format_sources(
        self, retrieved: List[SearchResult]
    ) -> List[Dict[str, Any]]:
        """Format sources for response."""
        sources = []

        for i, result in enumerate(retrieved):
            source = {
                "id": i + 1,
                "title": os.path.basename(result.source),
                "content_preview": result.content[:200] + "..." if len(result.content) > 200 else result.content,
                "score": round(result.score, 3),
                "metadata": result.metadata,
            }
            sources.append(source)

        return sources
