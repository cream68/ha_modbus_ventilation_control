from __future__ import annotations

def slugify(value: str) -> str:
    return value.casefold().replace(" ", "_")
