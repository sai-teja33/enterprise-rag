import re


SECTION_HEADING_PATTERNS = [
    # Numbered headings
    r"^\d+(\.\d+)*\s+.+$",

    # ALL CAPS headings
    r"^[A-Z][A-Z0-9 ,&()/\-]{3,}$",
]
def looks_like_heading(
    line: str,
    max_font_size: float | None = None,
    is_bold: bool = False,
) -> bool:

    if not line:
        return False

    line = line.strip()

    if len(line) < 3 or len(line) > 80:
        return False

    words = line.split()

    if len(words) > 6:
        return False

    # Obvious paragraph
    if line.endswith("."):
        return False

    if "," in line:
        return False

    common_words = {
        "is", "are", "was", "were",
        "may", "must", "should",
        "can", "will", "has", "have"
    }

    if any(w.lower() in common_words for w in words):
        return False

    # Numbered heading
    if re.match(r"^\d+(\.\d+)*\s+", line):
        return True

    # ALL CAPS
    if line.isupper():
        return True

    # Matches one of your heading regexes
    for pattern in SECTION_HEADING_PATTERNS:
        if re.match(pattern, line):
            return True

    # Simple Title Case heading
    if line == line.title():
        return True

    return False

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


def split_text_into_sections(text: str) -> list[dict]:
    """
    Split document into logical sections while preserving heading hierarchy.
    """

    if not text or not text.strip():
        return []

    lines = [line.rstrip() for line in text.splitlines()]

    sections = []

    current_title = "Introduction"
    current_lines = []

    current_level = 1

    # Stack of headings for hierarchy
    heading_stack = []

    parent_section = None

    for raw_line in lines:

        line = raw_line.strip()

        if not line:
            current_lines.append(raw_line)
            continue

        print(f"{line!r} -> {looks_like_heading(line)}")
        if looks_like_heading(line):

            # Flush previous section
            if current_lines:

                section_text = "\n".join(current_lines).strip()

                if section_text:
                    sections.append(
                        {
                            "section_title": current_title,
                            "section_text": section_text,
                            "heading_level": current_level,
                            "parent_section": parent_section,
                            "element_type": "paragraph",
                            "page_start": None,
                            "page_end": None,
                        }
                    )

            level = get_heading_level(line)

            while len(heading_stack) >= level:
                heading_stack.pop()

            parent_section = heading_stack[-1] if heading_stack else None

            current_title = line
            current_level = level
            current_lines = []

            heading_stack.append(current_title)

        else:
            current_lines.append(raw_line)

    # Flush final section
    if current_lines:

        section_text = "\n".join(current_lines).strip()

        if section_text:
            sections.append(
                {
                    "section_title": current_title,
                    "section_text": section_text,
                    "heading_level": current_level,
                    "parent_section": parent_section,
                    "element_type": "paragraph",
                    "page_start": None,
                    "page_end": None,
                }
            )

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

            # if current["section_title"] != section["section_title"]:
            #     current["section_title"] += " → " + section["section_title"]

            current["page_end"] = section.get("page_end", current["page_end"])

        else:
            merged.append(current)
            current = section.copy()

    merged.append(current)

    return merged