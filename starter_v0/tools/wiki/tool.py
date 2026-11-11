from __future__ import annotations

from typing import Any
from urllib.parse import quote

import requests

from tools._shared import TIMEOUT, err

ALLOWED_LANGS = ("vi", "en")
USER_AGENT = "AI20k-Day03-Research-Agent/1.0 (educational lab)"


def wiki_summary(title: str = "", lang: str = "vi") -> dict[str, Any]:
    """Get the lead summary of one Wikipedia article (no API key needed).

    Returns an error dict (never raises) for bad input, HTTP errors or missing articles.
    """
    try:
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title must be a non-empty string")
        lang = (lang or "vi").strip().lower() if isinstance(lang, str) else "vi"
        if lang not in ALLOWED_LANGS:
            raise ValueError(f"lang must be one of {list(ALLOWED_LANGS)}, got {lang!r}")

        clean_title = title.strip().replace(" ", "_")
        url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{quote(clean_title, safe='')}"
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        if response.status_code == 404:
            return {"tool": "wiki_summary", "title": title, "lang": lang, "items": [],
                    "error": "NotFound", "message": f"No Wikipedia article '{title}' on {lang}.wikipedia.org"}
        response.raise_for_status()
        data = response.json()
        page_url = ((data.get("content_urls") or {}).get("desktop") or {}).get("page") or url
        return {"tool": "wiki_summary", "title": title, "lang": lang, "items": [{
            "title": data.get("title") or title,
            "url": page_url,
            "source": f"{lang}.wikipedia.org",
            "summary": (data.get("extract") or "")[:2000],
        }]}
    except Exception as exc:
        return err("wiki_summary", exc)
