import re

def extract_citation_labels(markdown: str) -> list[str]:
    return sorted(set(re.findall(r"\[(S\d+)\]", markdown)))