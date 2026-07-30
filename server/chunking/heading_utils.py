import re
import statistics

SECTION_HEADING_PATTERNS = [
    # Numbered headings
    r"^\d+(\.\d+)*\s+.+$",

    # ALL CAPS headings
    r"^[A-Z][A-Z0-9 ,&()/\-]{3,}$",
]
HEADING_PROMOTION_RATIO = 1.15
HEADING_STARTERS = {
    "how", "what", "when", "where", "why",
    "can", "does", "do", "is", "are", "should",
    "may", "will", "could", "has", "have"
}
COMMON_HEADING_EXCLUSIONS = {
    "may", "must", "should", "can", "could", "will",
    "might", "shall", "unless", "however"
}

def looks_like_heading(
    line: str,
    max_font_size: float | None = None,
    median_font_size: float | None = None,
    is_bold: bool = False,
    element_type: str = "paragraph",
) -> bool:

    if not line:
        return False

    line = line.strip()

    if element_type in {"table", "list"}:
        return False

    if len(line) < 3 or len(line) > 80:
        return False

    words = line.split()

    if len(words) > 7:
        return False

    if line.endswith("."):
        return False

    if "," in line:
        return False

    if '→' in line or ':' in line:
        return False

    lower_line = line.lower()
    if any(keyword in lower_line for keyword in [
        'document no', 'policy no', 'version', 'effective date',
        'policy owner', 'applicability', 'review cycle', 'document id',
        'document status', 'page', 'date', 'owner'
    ]):
        return False

    if words[0].lower() in HEADING_STARTERS and len(words) > 3:
        return False

    if any(w.lower() in COMMON_HEADING_EXCLUSIONS for w in words):
        return False

    has_larger_font = (
        max_font_size is not None
        and median_font_size is not None
        and max_font_size >= median_font_size * HEADING_PROMOTION_RATIO
    )

    is_numbered = bool(re.match(r"^\d+(?:\.\d+)*\s+", line))
    is_all_caps = line.isupper() and len(line) > 4
    is_short_title = len(words) <= 5 and line == line.title()
    matches_heading_pattern = any(re.match(pattern, line) for pattern in SECTION_HEADING_PATTERNS)

    if median_font_size is None or max_font_size is None:
        # Fallback for documents without block metadata
        return is_numbered or is_all_caps or matches_heading_pattern

    if has_larger_font:
        return True

    if not is_bold:
        return False

    return is_numbered or is_all_caps or matches_heading_pattern or is_short_title

def get_heading_level(line: str) -> int:
    """
    Determine heading level.

    Examples
    --------
    1 Leave Policy              -> 1
    2.1 Sick Leave              -> 2
    2.1.3 Medical Certificate   -> 3
    """

    match = re.match(r"^\s*(\d+(?:\.\d+)*)", line)

    if match:
        return len(match.group(1).split("."))

    # Non-numbered headings are treated as H1
    return 1


def split_text_into_sections(
    text: str,
    blocks: list[dict] | None = None,
) -> list[dict]:
    """
    Split document into logical sections while preserving heading hierarchy.
    """

    if not text or not text.strip():
        return []

    lines = []
    median_font_size = None

    if blocks:
        font_sizes = [block.get("max_font_size") for block in blocks if block.get("max_font_size")]
        if font_sizes:
            median_font_size = statistics.median(font_sizes)

        for block in blocks:
            block_text = (block.get("text") or "").strip()
            element_type = block.get("element_type", "paragraph")
            max_font_size = block.get("max_font_size")
            is_bold = bool(block.get("is_bold", False))

            for raw_line in block_text.splitlines():
                line = raw_line.strip()
                if not line:
                    continue
                lines.append(
                    {
                        "text": line,
                        "max_font_size": max_font_size,
                        "median_font_size": median_font_size,
                        "is_bold": is_bold,
                        "element_type": element_type,
                    }
                )
    else:
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            lines.append(
                {
                    "text": line,
                    "max_font_size": None,
                    "median_font_size": None,
                    "is_bold": False,
                    "element_type": "paragraph",
                }
            )

    sections = []
    current_title = "Introduction"
    current_lines: list[str] = []
    current_level = 1
    heading_stack: list[str] = []
    parent_section = None
    current_element_type = "paragraph"

    def flush_section():
        section_text = "\n".join(current_lines).strip()
        if not section_text:
            return

        sections.append(
            {
                "section_title": current_title,
                "section_text": section_text,
                "heading_level": current_level,
                "parent_section": parent_section,
                "element_type": current_element_type,
                "page_start": None,
                "page_end": None,
            }
        )

    for line_item in lines:
        raw_line = line_item["text"]

        if looks_like_heading(
            raw_line,
            max_font_size=line_item.get("max_font_size"),
            median_font_size=line_item.get("median_font_size"),
            is_bold=line_item.get("is_bold", False),
            element_type=line_item.get("element_type", "paragraph"),
        ):

            if current_lines:
                flush_section()
                current_lines = []

            level = get_heading_level(raw_line)
            while len(heading_stack) >= level:
                heading_stack.pop()

            parent_section = heading_stack[-1] if heading_stack else None
            current_title = raw_line
            current_level = level
            current_element_type = line_item.get("element_type", "heading")
            heading_stack.append(current_title)
            continue

        current_lines.append(raw_line)
        current_element_type = current_element_type or line_item.get("element_type", "paragraph")

    if current_lines:
        flush_section()

    if not sections:
        sections.append(
            {
                "section_title": "Full Document",
                "section_text": text.strip(),
                "heading_level": 1,
                "parent_section": None,
                "element_type": "paragraph",
                "page_start": None,
                "page_end": None,
            }
        )

    return sections


def merge_small_sections(
    sections: list[dict],
    min_chars: int = 700,
) -> list[dict]:
    """
    Merge consecutive small sections while preserving metadata.
    """

    if not sections:
        return []

    merged = []

    current = sections[0].copy()

    for section in sections[1:]:

        if len(current["section_text"]) < min_chars:

            current["section_text"] += "\n\n" + section["section_text"]

            if current["section_title"] != section["section_title"]:
                if current["section_title"] in {"Introduction", "Full Document"}:
                    current["section_title"] = section["section_title"]
                else:
                    current["section_title"] = f"{current['section_title']} → {section['section_title']}"

            current["heading_level"] = min(current["heading_level"], section["heading_level"])
            current["parent_section"] = current["parent_section"] or section.get("parent_section")
            current["page_end"] = section.get("page_end", current["page_end"])

        else:
            merged.append(current)
            current = section.copy()

    merged.append(current)

    return merged