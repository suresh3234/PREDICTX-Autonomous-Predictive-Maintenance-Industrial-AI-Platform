import json
import re
from pathlib import Path
from typing import Any


class DocumentParser:
    """
    Multi-format industrial equipment document parser.
    Extracts text sections and metadata from JSON, Markdown, and plain text manuals.
    """

    @staticmethod
    def parse_file(file_path: str | Path) -> list[dict[str, Any]]:
        """Parses a document file based on its extension."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document file not found at: {file_path}")

        suffix = path.suffix.lower()
        if suffix == ".json":
            return DocumentParser.parse_json_file(path)
        elif suffix in [".md", ".markdown"]:
            return DocumentParser.parse_markdown_file(path)
        else:
            return DocumentParser.parse_text_file(path)

    @staticmethod
    def parse_json_file(file_path: Path) -> list[dict[str, Any]]:
        """Parses structured JSON manual files."""
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            docs = []
            for item in data:
                doc_id = item.get("id") or item.get("document_id") or f"doc_{len(docs)+1}"
                text = item.get("text") or item.get("content") or ""
                metadata = item.get("metadata", {})
                docs.append({
                    "id": doc_id,
                    "text": text.strip(),
                    "metadata": {
                        "source": str(file_path.name),
                        **metadata,
                    },
                })
            return docs
        elif isinstance(data, dict):
            return [{
                "id": data.get("id", "doc_1"),
                "text": (data.get("text") or data.get("content", "")).strip(),
                "metadata": {"source": str(file_path.name), **data.get("metadata", {})},
            }]
        return []

    @staticmethod
    def parse_markdown(text: str, source_name: str = "manual.md") -> list[dict[str, Any]]:
        """
        Parses Markdown text into hierarchical sections based on headings (#, ##, ###).
        """
        sections = []
        lines = text.splitlines()
        current_heading = "General Procedures"
        current_level = 1
        current_lines = []

        for line in lines:
            heading_match = re.match(r"^(#{1,6})\s+(.*)$", line)
            if heading_match:
                # Flush previous section
                if current_lines:
                    sec_text = "\n".join(current_lines).strip()
                    if sec_text:
                        sections.append({
                            "id": f"{source_name}_{len(sections)+1}",
                            "text": f"{current_heading}:\n{sec_text}",
                            "metadata": {
                                "source": source_name,
                                "section": current_heading,
                                "heading_level": current_level,
                            },
                        })
                    current_lines = []

                current_level = len(heading_match.group(1))
                current_heading = heading_match.group(2).strip()
            else:
                current_lines.append(line)

        # Flush final section
        if current_lines:
            sec_text = "\n".join(current_lines).strip()
            if sec_text:
                sections.append({
                    "id": f"{source_name}_{len(sections)+1}",
                    "text": f"{current_heading}:\n{sec_text}",
                    "metadata": {
                        "source": source_name,
                        "section": current_heading,
                        "heading_level": current_level,
                    },
                })

        return sections

    @staticmethod
    def parse_markdown_file(file_path: Path) -> list[dict[str, Any]]:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        return DocumentParser.parse_markdown(content, source_name=file_path.name)

    @staticmethod
    def parse_text_file(file_path: Path) -> list[dict[str, Any]]:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        # Split by double newline paragraphs
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        return [
            {
                "id": f"{file_path.stem}_p{idx+1}",
                "text": p,
                "metadata": {"source": file_path.name, "paragraph_index": idx + 1},
            }
            for idx, p in enumerate(paragraphs)
        ]
