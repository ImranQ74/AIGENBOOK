"""
Document processor for chunking and preparing textbook content for RAG.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""

    content: str
    source: str
    chunk_id: str
    start_char: int
    end_char: int
    section_title: str = ""


class DocumentProcessor:
    """
    Processes documents into chunks for RAG indexing.
    Optimized for textbook content with code examples.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        max_chunk_size: int = 1000,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_chunk_size = max_chunk_size

    def process_file(self, file_path: str) -> List[TextChunk]:
        """
        Process a single file and return chunks.

        Args:
            file_path: Path to the file to process

        Returns:
            List of TextChunk objects
        """
        path = Path(file_path)

        # Read file content
        content = self._read_file(file_path)

        # Extract metadata from frontmatter
        frontmatter = self._parse_frontmatter(content)

        # Get main content without frontmatter
        main_content = content

        # Detect document type and process accordingly
        if path.suffix == ".md" or path.suffix == ".mdx":
            chunks = self._process_markdown(main_content, str(path), frontmatter)
        else:
            chunks = self._process_text(main_content, str(path))

        return chunks

    def _read_file(self, file_path: str) -> str:
        """Read file content with proper encoding."""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """Parse YAML frontmatter from markdown."""
        frontmatter = {}

        if content.startswith("---"):
            end_idx = content.find("---", 3)
            if end_idx > 0:
                yaml_content = content[3:end_idx]
                # Simple YAML parsing
                for line in yaml_content.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        frontmatter[key.strip()] = value.strip()

        return frontmatter

    def _process_markdown(self, content: str, source: str, frontmatter: Dict) -> List[TextChunk]:
        """
        Process markdown content into chunks.
        Preserves code blocks and headers as atomic units.
        """
        chunks = []

        # Remove frontmatter
        if content.startswith("---"):
            end_idx = content.find("---", 3)
            if end_idx > 0:
                content = content[end_idx + 3 :]

        # Split into sections by headers
        sections = self._split_by_headers(content)

        for section in sections:
            section_chunks = self._chunk_section(
                section["content"],
                source,
                section["title"],
                frontmatter,
            )
            chunks.extend(section_chunks)

        return chunks

    def _split_by_headers(self, content: str) -> List[Dict]:
        """Split markdown content by headers."""
        lines = content.split("\n")
        sections = []
        current_section = {"title": "", "content": []}
        current_title = ""

        for line in lines:
            # Check for header
            header_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if header_match:
                # Save previous section
                if current_section["content"]:
                    sections.append(current_section)

                # Start new section
                current_title = header_match.group(2).strip()
                current_section = {
                    "title": current_title,
                    "content": [line],
                }
            else:
                current_section["content"].append(line)

        # Don't forget last section
        if current_section["content"]:
            sections.append(current_section)

        return sections

    def _chunk_section(
        self,
        lines: List[str],
        source: str,
        section_title: str,
        frontmatter: Dict,
    ) -> List[TextChunk]:
        """Chunk a section of content."""
        chunks = []
        content = "\n".join(lines)

        # First, extract and preserve code blocks
        code_blocks = []
        content_without_code = content

        # Simple code block extraction
        code_pattern = r"```[\s\S]*?```"
        for i, match in enumerate(re.finditer(code_pattern, content)):
            code_blocks.append(
                {
                    "placeholder": f"__CODE_BLOCK_{i}__",
                    "content": match.group(),
                }
            )

        # Replace code blocks with placeholders
        for block in code_blocks:
            content_without_code = content_without_code.replace(block["content"], block["placeholder"])

        # Split into paragraphs
        paragraphs = content_without_code.split("\n\n")
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        current_chunk = ""
        chunk_start = 0
        char_count = 0

        for para in paragraphs:
            para = para.strip()

            # Handle placeholders
            for block in code_blocks:
                para = para.replace(block["placeholder"], "\n```\n")

            # Check if adding this paragraph would exceed chunk size
            if char_count + len(para) > self.chunk_size and current_chunk:
                # Create chunk
                chunk = self._create_chunk(current_chunk, source, chunk_start, char_count, section_title)
                chunks.append(chunk)

                # Handle overlap
                if self.chunk_overlap > 0:
                    overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                    current_chunk = current_chunk[overlap_start:]
                    char_count = len(current_chunk)
                else:
                    current_chunk = ""
                    char_count = 0

            current_chunk += para + "\n\n"
            char_count += len(para) + 2

        # Don't forget last chunk
        if current_chunk.strip():
            chunk = self._create_chunk(current_chunk, source, chunk_start, char_count, section_title)
            chunks.append(chunk)

        return chunks

    def _create_chunk(
        self,
        content: str,
        source: str,
        start_char: int,
        end_char: int,
        section_title: str,
    ) -> TextChunk:
        """Create a TextChunk object."""
        # Clean up content
        content = content.strip()

        # Generate unique ID
        import hashlib

        chunk_id = hashlib.md5(f"{source}:{start_char}:{end_char}".encode()).hexdigest()[:12]

        return TextChunk(
            content=content,
            source=source,
            chunk_id=chunk_id,
            start_char=start_char,
            end_char=end_char,
            section_title=section_title,
        )

    def _process_text(self, content: str, source: str) -> List[TextChunk]:
        """Process plain text content."""
        chunks = []

        # Simple sliding window chunking
        chars = list(content)
        start = 0

        while start < len(chars):
            end = min(start + self.chunk_size, len(chars))

            # Try to break at sentence boundary
            while end > start and chars[end - 1] not in ".!?":
                end -= 1

            # If no sentence boundary, break at word
            if end == start:
                while end < len(chars) and chars[end] not in " \n":
                    end += 1

            chunk_content = "".join(chars[start:end])

            if chunk_content.strip():
                import hashlib

                chunk_id = hashlib.md5(f"{source}:{start}:{end}".encode()).hexdigest()[:12]

                chunks.append(
                    TextChunk(
                        content=chunk_content.strip(),
                        source=source,
                        chunk_id=chunk_id,
                        start_char=start,
                        end_char=end,
                    )
                )

            start = end - self.chunk_overlap if self.chunk_overlap > 0 else end

        return chunks
