import re


SECTION_HEADING_PATTERNS = [
    # Numbered headings like "1 Leave Policy", "2.1 Sick Leave"
    r"^\s*\d+(\.\d+)*\s+[A-Z][A-Za-z0-9 ,&()/-]{2,}$",

    # ALL CAPS headings like "LEAVE POLICY"
    r"^\s*[A-Z][A-Z0-9 ,&()/-]{3,}\s*$",

    # Title case headings like "Leave Policy", "Earned Leave", "Emergency Leave"
    r"^\s*[A-Z][A-Za-z0-9/&()\-]+(?:\s+[A-Z][A-Za-z0-9/&()\-]+){0,8}\s*$"
]


def looks_like_heading(line: str) -> bool:
    if not line:
        return False

    line = line.strip()

    if len(line) < 3 or len(line) > 120:
        return False

    if len(line.split()) > 12:
        return False

    # avoid treating normal sentences as headings
    if line.endswith("."):
        return False

    for pattern in SECTION_HEADING_PATTERNS:
        if re.match(pattern, line):
            return True

    return False


def split_text_into_sections(text: str) -> list[dict]:
    """
    Splits a text blob into sections based on heading-like lines.

    Returns:
    [
        {
            "section_title": "Leave Policy",
            "section_text": "...."
        },
        ...
    ]
    """
    if not text or not text.strip():
        return []

    lines = [line.rstrip() for line in text.splitlines()]

    sections = []
    current_title = "Introduction"
    current_lines = []

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            current_lines.append(raw_line)
            continue

        if looks_like_heading(line):
            # flush previous section
            if current_lines:
                section_text = "\n".join(current_lines).strip()
                if section_text:
                    sections.append({
                        "section_title": current_title,
                        "section_text": section_text
                    })
            current_title = line
            current_lines = []
        else:
            current_lines.append(raw_line)

    # flush last section
    if current_lines:
        section_text = "\n".join(current_lines).strip()
        if section_text:
            sections.append({
                "section_title": current_title,
                "section_text": section_text
            })

    if not sections:
        sections.append({
            "section_title": "Full Document",
            "section_text": text.strip()
        })

    return sections