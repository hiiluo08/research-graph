import re

import httpx


def fetch_url_text(url: str, max_chars: int = 12000) -> str:
    response = httpx.get(url, timeout=20, follow_redirects=True)
    response.raise_for_status()
    text = response.text
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]