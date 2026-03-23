#!/usr/bin/env python3

from __future__ import annotations

import datetime as dt
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

import yaml
from scholarly import scholarly


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "_config.yml"
PUBLICATIONS_PATH = ROOT / "_data" / "publications.yml"
OVERRIDES_PATH = ROOT / "_data" / "publication_overrides.yml"

SCALAR_FIELDS_TO_MERGE = (
    "doi",
    "source_url",
    "summary",
    "abstract",
    "kind",
    "featured",
    "selected",
    "cover_image",
    "cover_alt",
)

LINK_FIELDS = ("paper", "pdf", "project", "code", "dataset", "slides", "video")


def load_yaml(path: Path, default: Any) -> Any:
    if not path.exists():
        return default

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return default if data is None else data


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.lower()).strip("-")
    return normalized or "publication"


def normalize_title(value: str | None) -> str | None:
    if not value:
        return None
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-zA-Z0-9]+", "", normalized.lower())
    return normalized or None


def normalize_doi(raw_value: str | None) -> str | None:
    if not raw_value:
        return None

    cleaned = raw_value.strip()
    cleaned = re.sub(r"^https?://(dx\.)?doi\.org/", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^doi\.org/", "", cleaned, flags=re.IGNORECASE)
    return cleaned or None


def split_authors(raw_authors: str | None) -> list[str]:
    if not raw_authors:
        return []

    if " and " in raw_authors:
        pieces = re.split(r"\s+and\s+", raw_authors)
    else:
        pieces = raw_authors.split(",")

    return [author.strip() for author in pieces if author.strip()]


def normalize_person_name(name: str) -> tuple[str, str]:
    pieces = re.findall(r"[a-z0-9]+", slugify(name))
    if not pieces:
        return "", ""
    return pieces[0], pieces[-1]


def matches_target_author(author_name: str, variants: list[str]) -> bool:
    author_first, author_last = normalize_person_name(author_name)
    if not author_last:
        return False

    for variant in variants:
        variant_first, variant_last = normalize_person_name(variant)
        if not variant_last or author_last != variant_last:
            continue
        if author_first == variant_first:
            return True
        if author_first[:1] and variant_first[:1] and author_first[:1] == variant_first[:1]:
            return True

    return False


def find_author_position(authors: list[str], variants: list[str]) -> int | None:
    for index, author_name in enumerate(authors, start=1):
        if matches_target_author(author_name, variants):
            return index
    return None


def scholar_publication_url(user_id: str, publication_id: str | None) -> str | None:
    if not publication_id:
        return None
    citation_for_view = publication_id if ":" in publication_id else f"{user_id}:{publication_id}"
    return (
        "https://scholar.google.com/citations"
        f"?view_op=view_citation&hl=en&user={user_id}&citation_for_view={citation_for_view}"
    )


def cited_by_url(cites_id: Any) -> str | None:
    if isinstance(cites_id, list):
        cites_id = cites_id[0] if cites_id else None
    if not cites_id:
        return None
    return f"https://scholar.google.com/scholar?cites={cites_id}"


def first_present(mapping: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        value = mapping.get(key)
        if value:
            return value
    return None


def merge_manual_fields(base: dict[str, Any], extra: dict[str, Any] | None) -> dict[str, Any]:
    if not extra:
        return base

    merged = dict(base)

    for field in SCALAR_FIELDS_TO_MERGE:
        value = extra.get(field)
        if value:
            merged[field] = value

    badges = list(merged.get("badges") or [])
    for badge in extra.get("badges") or []:
        if badge not in badges:
            badges.append(badge)
    if badges:
        merged["badges"] = badges

    links = dict(merged.get("links") or {})
    for field in LINK_FIELDS:
        value = (extra.get("links") or {}).get(field)
        if value:
            links[field] = value
    if links:
        merged["links"] = links

    return merged


def compact_entry(entry: dict[str, Any]) -> dict[str, Any]:
    compacted: dict[str, Any] = {}
    for key, value in entry.items():
        if value in (None, "", [], {}):
            continue
        compacted[key] = value
    return compacted


def find_matching_existing_entry(
    *,
    scholar_id: str | None,
    doi: str | None,
    title: str | None,
    by_scholar_id: dict[str, dict[str, Any]],
    by_doi: dict[str, dict[str, Any]],
    by_title: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    if scholar_id and scholar_id in by_scholar_id:
        return by_scholar_id[scholar_id]

    normalized_doi = normalize_doi(doi)
    if normalized_doi and normalized_doi in by_doi:
        return by_doi[normalized_doi]

    normalized_title = normalize_title(title)
    if normalized_title and normalized_title in by_title:
        return by_title[normalized_title]

    return None


def main() -> int:
    config = load_yaml(CONFIG_PATH, {})
    scholar_config = config.get("scholar", {})
    author_config = config.get("author", {})

    scholar_user_id = scholar_config.get("user_id")
    if not scholar_user_id:
        print("Missing scholar.user_id in _config.yml", file=sys.stderr)
        return 1

    name_variants = list(author_config.get("name_variants") or [])
    for key in ("full_name", "short_name"):
        if author_config.get(key):
            name_variants.append(author_config[key])

    existing_data = load_yaml(PUBLICATIONS_PATH, {"items": []})
    overrides = load_yaml(OVERRIDES_PATH, {})
    existing_items = existing_data.get("items", [])
    existing_by_scholar_id = {
        item.get("scholar_id"): item for item in existing_items if item.get("scholar_id")
    }
    existing_by_doi = {
        normalize_doi(item.get("doi")): item
        for item in existing_items
        if normalize_doi(item.get("doi"))
    }
    existing_by_title = {
        normalize_title(item.get("title")): item
        for item in existing_items
        if normalize_title(item.get("title"))
    }

    author = scholarly.search_author_id(scholar_user_id)
    author = scholarly.fill(author, sections=["publications"])

    synced_items: list[dict[str, Any]] = []

    for publication in author.get("publications", []):
        filled_publication = scholarly.fill(publication)
        bib = filled_publication.get("bib", {})
        title = bib.get("title")
        if not title:
            continue

        authors = split_authors(bib.get("author"))
        slug = slugify(title)
        scholar_id = filled_publication.get("author_pub_id")
        doi = normalize_doi(bib.get("doi"))
        base_entry = {
            "slug": slug,
            "scholar_id": scholar_id,
            "title": title,
            "authors": authors,
            "authors_text": ", ".join(authors),
            "author_position": find_author_position(authors, name_variants),
            "venue": first_present(
                bib,
                ("journal", "conference", "booktitle", "publisher", "publication", "venue"),
            ),
            "year": int(bib["pub_year"]) if bib.get("pub_year") else None,
            "citations": filled_publication.get("num_citations")
            or filled_publication.get("citedby")
            or 0,
            "scholar_url": scholar_publication_url(scholar_user_id, scholar_id),
            "cited_by_url": cited_by_url(filled_publication.get("cites_id")),
            "source_url": first_present(
                filled_publication,
                ("pub_url", "eprint_url", "url_scholarbib"),
            ),
            "doi": doi,
            "abstract": bib.get("abstract"),
        }

        existing_entry = find_matching_existing_entry(
            scholar_id=scholar_id,
            doi=doi,
            title=title,
            by_scholar_id=existing_by_scholar_id,
            by_doi=existing_by_doi,
            by_title=existing_by_title,
        )

        merged_entry = merge_manual_fields(base_entry, existing_entry)
        merged_entry = merge_manual_fields(merged_entry, overrides.get(slug))
        synced_items.append(compact_entry(merged_entry))

    synced_items.sort(key=lambda item: (-int(item.get("year", 0)), item.get("title", "")))

    payload = {
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "source": "google-scholar",
        "items": synced_items,
    }

    with PUBLICATIONS_PATH.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(
            payload,
            handle,
            sort_keys=False,
            allow_unicode=True,
            width=88,
        )

    print(f"Synced {len(synced_items)} publications to {PUBLICATIONS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
