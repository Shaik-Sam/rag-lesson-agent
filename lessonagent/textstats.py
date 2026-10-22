import re
from dataclasses import dataclass
from typing import List

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'\u2019-]*")
ALPHA_RE = re.compile(r"[A-Za-z][A-Za-z'\u2019-]*")


@dataclass
class Section:
    title: str
    level: int
    lines: List[str]


def parse_sections(text):
    sections = []
    current = Section("", 0, [])
    for line in text.splitlines():
        match = HEADING_RE.match(line)
        if match:
            sections.append(current)
            current = Section(match.group(2).strip(), len(match.group(1)), [])
        else:
            current.lines.append(line)
    sections.append(current)
    return [s for s in sections if s.title or any(l.strip() for l in s.lines)]


def clean_line(line):
    line = re.sub(r"`([^`]*)`", r"\1", line)
    line = re.sub(r"\*\*|__|\*", "", line)
    line = re.sub(r"^\s*(?:[-+\u2022]|\d+[.)])\s+", "", line)
    line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)
    return line.strip()


def sentences_from_lines(lines):
    out = []
    for line in lines:
        cleaned = clean_line(line)
        if not cleaned:
            continue
        parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"\u201c\[(])", cleaned)
        out.extend(p.strip() for p in parts if p.strip())
    return out


def all_sentences(text, skip_title_pattern=None):
    lines = []
    for section in parse_sections(text):
        if skip_title_pattern and re.search(skip_title_pattern, section.title, re.IGNORECASE):
            continue
        lines.extend(section.lines)
    return sentences_from_lines(lines)


def count_syllables(word):
    word = re.sub(r"[^a-z]", "", word.lower())
    if not word:
        return 0
    if len(word) <= 3:
        return 1
    word = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", word)
    word = re.sub(r"^y", "", word)
    return max(1, len(re.findall(r"[aeiouy]{1,2}", word)))


def word_tokens(text):
    return TOKEN_RE.findall(text)


def word_count(text):
    body = []
    for section in parse_sections(text):
        body.extend(section.lines)
    return len(word_tokens(" ".join(clean_line(l) for l in body)))


def flesch_kincaid_grade(sentences):
    if not sentences:
        return 0.0
    words = []
    for sentence in sentences:
        words.extend(ALPHA_RE.findall(sentence))
    if not words:
        return 0.0
    syllables = sum(count_syllables(w) for w in words)
    return 0.39 * (len(words) / len(sentences)) + 11.8 * (syllables / len(words)) - 15.59


def sentence_lengths(sentences):
    return [len(word_tokens(s)) for s in sentences]


def shorten(text, limit=140):
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 3] + "..."
