#!/usr/bin/env python3
"""
Project to PDF Converter
Generates a PDF containing the folder structure and all code files from a project directory.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Preformatted,
)
from reportlab.lib.enums import TA_LEFT

# Common directories and files to ignore
IGNORE_PATTERNS = {
    # Version control
    ".git",
    ".svn",
    ".hg",
    # Dependencies
    "node_modules",
    "vendor",
    "venv",
    "env",
    ".venv",
    # Build outputs
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    "target",
    ".next",
    "out",
    ".nuxt",
    ".output",
    # IDE
    ".vscode",
    ".idea",
    ".vs",
    # OS
    ".DS_Store",
    "Thumbs.db",
    # Other
    ".env",
    ".env.local",
    "coverage",
    ".coverage",
}

# File extensions to include (code files)
CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".cs",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".swift",
    ".kt",
    ".scala",
    ".html",
    ".css",
    ".scss",
    ".sass",
    ".less",
    ".json",
    ".xml",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".sh",
    ".bash",
    ".zsh",
    ".fish",
    ".sql",
    ".md",
    ".txt",
    ".rst",
    ".vue",
    ".svelte",
    ".astro",
}


def should_ignore(path):
    """Check if a path should be ignored."""
    name = os.path.basename(path)
    return name in IGNORE_PATTERNS or name.startswith(".")


def get_folder_structure(root_path, prefix="", is_last=True):
    """Generate a tree-like folder structure."""
    lines = []
    root_path = Path(root_path)

    try:
        items = sorted(
            root_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())
        )
        items = [item for item in items if not should_ignore(item)]

        for i, item in enumerate(items):
            is_last_item = i == len(items) - 1
            connector = "└── " if is_last_item else "├── "
            lines.append(f"{prefix}{connector}{item.name}")

            if item.is_dir():
                extension = "    " if is_last_item else "│   "
                lines.extend(
                    get_folder_structure(item, prefix + extension, is_last_item)
                )
    except PermissionError:
        pass

    return lines


def get_all_code_files(root_path):
    """Get all code files recursively."""
    code_files = []
    root_path = Path(root_path)

    for item in root_path.rglob("*"):
        if item.is_file() and item.suffix in CODE_EXTENSIONS:
            # Check if any parent directory should be ignored
            if not any(should_ignore(parent) for parent in item.parents):
                if not should_ignore(item):
                    code_files.append(item)

    return sorted(code_files, key=lambda x: str(x))


def read_file_content(file_path):
    """Read file content with fallback for encoding issues."""
    encodings = ["utf-8", "latin-1", "cp1252"]

    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue

    # If all encodings fail, read as binary and decode with errors='ignore'
    with open(file_path, "rb") as f:
        return f.read().decode("utf-8", errors="ignore")


def create_pdf(root_path, output_file="project_documentation.pdf"):
    """Create PDF with project structure and code."""
    root_path = Path(root_path).resolve()

    # Create PDF document
    doc = SimpleDocTemplate(
        output_file,
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_LEFT,
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=12,
        textColor="#2c3e50",
    )
    code_style = ParagraphStyle(
        "Code", parent=styles["Code"], fontSize=8, leftIndent=20, spaceAfter=6
    )

    # Title
    title = Paragraph(f"Project Documentation: {root_path.name}", title_style)
    elements.append(title)

    # Metadata
    meta_text = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
    meta_text += f"Root Path: {root_path}"
    elements.append(Paragraph(meta_text, styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    # Folder Structure
    elements.append(Paragraph("Folder Structure", heading_style))
    elements.append(Spacer(1, 0.1 * inch))

    structure = get_folder_structure(root_path)
    structure_text = root_path.name + "\n" + "\n".join(structure)

    # Use Preformatted for better tree structure rendering
    structure_pre = Preformatted(structure_text, styles["Code"], maxLineLength=100)
    elements.append(structure_pre)
    elements.append(PageBreak())

    # Code Files
    elements.append(Paragraph("Code Files", heading_style))
    elements.append(Spacer(1, 0.2 * inch))

    code_files = get_all_code_files(root_path)

    if not code_files:
        elements.append(Paragraph("No code files found.", styles["Normal"]))
    else:
        for file_path in code_files:
            relative_path = file_path.relative_to(root_path)

            # File header
            file_header = Paragraph(f"<b>File: {relative_path}</b>", heading_style)
            elements.append(file_header)
            elements.append(Spacer(1, 0.1 * inch))

            # File content
            try:
                content = read_file_content(file_path)

                # Limit very large files
                if len(content) > 50000:
                    content = (
                        content[:50000] + "\n\n... (file truncated, too large) ..."
                    )

                # Escape special characters for XML/HTML
                content = (
                    content.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )

                # Split into chunks to avoid reportlab issues with very long paragraphs
                lines = content.split("\n")
                for i in range(0, len(lines), 100):
                    chunk = "\n".join(lines[i : i + 100])
                    code_para = Preformatted(chunk, styles["Code"], maxLineLength=95)
                    elements.append(code_para)

            except Exception as e:
                error_text = f"Error reading file: {str(e)}"
                elements.append(Paragraph(error_text, styles["Normal"]))

            elements.append(Spacer(1, 0.2 * inch))
            elements.append(PageBreak())

    # Build PDF
    print(f"Generating PDF: {output_file}")
    print(f"Processing {len(code_files)} code files...")

    doc.build(elements)
    print(f"✓ PDF generated successfully: {output_file}")


def main():
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        root_path = "."

    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = "project_documentation.pdf"

    root_path = Path(root_path).resolve()

    if not root_path.exists():
        print(f"Error: Path '{root_path}' does not exist.")
        sys.exit(1)

    if not root_path.is_dir():
        print(f"Error: Path '{root_path}' is not a directory.")
        sys.exit(1)

    print(f"Project root: {root_path}")
    print(f"Output file: {output_file}")
    print()

    create_pdf(root_path, output_file)


if __name__ == "__main__":
    main()
