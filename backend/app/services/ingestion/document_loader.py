"""
document_loader.py — reads the policy .md files and cuts them into CHUNKS.

CONCEPT — Chunking (first step of RAG):
  We don't search whole documents; we search small pieces ("chunks").
  ANALOGY: If someone asks "what is BANK_TIMEOUT?", you hand them the one
  paragraph that answers it, not the whole 3-page guide.

  Our documents use "## " headings for each section, so the
  simplest good chunk = one section = one heading + its paragraph.
"""

from dataclasses import dataclass

from app.config.settings import settings


@dataclass
class Chunk:
    chunk_id: str    # e.g. "payment_failure_operations_guide#2"
    document: str    # file name without .md
    section: str     # the "## " heading text
    text: str        # heading + body (what we search and show the AI)


def load_chunks() -> list[Chunk]:
    chunks: list[Chunk] = []
    docs_dir = settings.data_dir / "documents"

    for path in sorted(docs_dir.glob("*.md")):
        document = path.stem
        content = path.read_text(encoding="utf-8")

        # Split on "\n## " so each piece starts with one section heading.
        # parts[0] is the title block before the first section; we skip it.
        parts = content.split("\n## ")[1:]

        for number, part in enumerate(parts, start=1):
            heading, _, body = part.partition("\n")
            # Join wrapped lines into one clean paragraph.
            body = " ".join(line.strip() for line in body.splitlines() if line.strip())
            section = heading.strip()
            chunks.append(
                Chunk(
                    chunk_id=f"{document}#{number}",
                    document=document,
                    section=section,
                    text=f"{section}. {body}",
                )
            )
    return chunks
