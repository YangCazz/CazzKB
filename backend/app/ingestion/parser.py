from dataclasses import dataclass, field
from enum import Enum
import re


class ElementType(str, Enum):
    HEADER = "header"
    CODE = "code"
    TABLE = "table"
    MATH = "math"
    LIST = "list"
    BLOCKQUOTE = "blockquote"
    TEXT = "text"
    MERMAID = "mermaid"
    FRONTMATTER = "frontmatter"


@dataclass
class Element:
    content: str
    type: ElementType
    level: int = 0              # header level (1-6)
    header_path: str = ""       # full path at this element
    meta: dict = field(default_factory=dict)


def parse_markdown(text: str) -> list[Element]:
    """Parse markdown into semantic elements."""
    elements: list[Element] = []
    lines = text.split("\n")
    header_stack: list[str] = []

    def current_header_path() -> str:
        return "/" + "/".join(header_stack) if header_stack else ""

    i = 0
    # Extract YAML frontmatter first
    if lines and lines[0].strip() == "---":
        end_idx = 1
        while end_idx < len(lines) and lines[end_idx].strip() != "---":
            end_idx += 1
        if end_idx < len(lines):
            fm_content = "\n".join(lines[1:end_idx])
            elements.append(Element(content=fm_content, type=ElementType.FRONTMATTER))
            lines = lines[end_idx + 1:]

    while i < len(lines):
        line = lines[i]

        # Blank line
        if not line.strip():
            i += 1
            continue

        # Code blocks (fenced)
        if line.strip().startswith("```"):
            fence_start = i
            fence_marker = line.strip()
            lang = fence_marker[3:].strip().lower()
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                i += 1
            code_content = "\n".join(lines[fence_start + 1:i])
            etype = ElementType.MERMAID if lang == "mermaid" else ElementType.CODE
            elements.append(Element(
                content=code_content, type=etype,
                header_path=current_header_path(),
                meta={"language": lang},
            ))
            i += 1  # skip closing fence
            continue

        # Math blocks ($$...$$)
        if line.strip().startswith("$$"):
            math_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("$$"):
                math_lines.append(lines[i])
                i += 1
            elements.append(Element(
                content="\n".join(math_lines), type=ElementType.MATH,
                header_path=current_header_path(),
            ))
            i += 1
            continue

        # Headers
        header_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if header_match:
            level = len(header_match.group(1))
            title = header_match.group(2).strip()

            # Update header stack
            while len(header_stack) >= level:
                header_stack.pop()
            header_stack.append(title)

            elements.append(Element(
                content=title, type=ElementType.HEADER,
                level=level, header_path=current_header_path(),
            ))
            i += 1
            continue

        # Tables: detect pipe-delimited lines
        if "|" in line and i + 1 < len(lines) and re.match(r"^[\|\s\-:]+$", lines[i + 1].strip()):
            table_lines = [line]
            i += 1
            # separator line
            if i < len(lines):
                table_lines.append(lines[i])
                i += 1
            # data rows
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                table_lines.append(lines[i])
                i += 1
            elements.append(Element(
                content="\n".join(table_lines), type=ElementType.TABLE,
                header_path=current_header_path(),
            ))
            continue

        # Blockquotes
        if line.startswith(">"):
            quote_lines = []
            while i < len(lines) and (lines[i].startswith(">") or
                                       (lines[i].strip() == "" and i + 1 < len(lines) and lines[i + 1].startswith(">"))):
                if lines[i].strip():
                    quote_lines.append(lines[i])
                i += 1
            elements.append(Element(
                content="\n".join(quote_lines), type=ElementType.BLOCKQUOTE,
                header_path=current_header_path(),
            ))
            continue

        # Lists (unordered or ordered)
        if re.match(r"^(\s{0,3})([-*+]|\d+\.)\s", line):
            list_lines = []
            while i < len(lines):
                stripped = lines[i].strip()
                if not stripped:
                    # peek ahead: continue if next line is list item
                    if i + 1 < len(lines) and re.match(r"^(\s{0,3})([-*+]|\d+\.)\s", lines[i + 1]):
                        list_lines.append(lines[i])
                        i += 1
                        continue
                    break
                if re.match(r"^(\s{0,3})([-*+]|\d+\.)\s", lines[i]):
                    list_lines.append(lines[i])
                    i += 1
                elif lines[i].startswith("  ") or lines[i].startswith("\t"):
                    # continuation line
                    list_lines.append(lines[i])
                    i += 1
                else:
                    break
            elements.append(Element(
                content="\n".join(list_lines), type=ElementType.LIST,
                header_path=current_header_path(),
            ))
            continue

        # Regular text paragraph
        text_lines = []
        while i < len(lines) and lines[i].strip() and \
                not lines[i].strip().startswith("```") and \
                not lines[i].strip().startswith("$$") and \
                not re.match(r"^(#{1,6})\s", lines[i]) and \
                not ("|" in lines[i] and i + 1 < len(lines) and re.match(r"^[\|\s\-:]+$", lines[i + 1].strip())) and \
                not lines[i].startswith(">") and \
                not re.match(r"^(\s{0,3})([-*+]|\d+\.)\s", lines[i]):
            text_lines.append(lines[i])
            i += 1
        elements.append(Element(
            content="\n".join(text_lines), type=ElementType.TEXT,
            header_path=current_header_path(),
        ))

    return elements
