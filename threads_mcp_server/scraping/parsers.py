"""HTML/JSON parsers for threads.net profile pages.

Threads.net ships profile + thread data as embedded JSON inside
``<script type=\"application/json\">`` blocks (Next.js ``pageProps``). The
parsers here do a **recursive deep-scan**: they walk every parsed JSON blob
and collect nodes that look like a user or a thread by structural shape. This
is deliberately resilient to Facebook/Meta shuffling field names one level
deeper in the tree, and every extractor is unit-testable with a fixture.
"""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)

_SCRIPT_RE = re.compile(r"<script[^>]*>(.*?)</script>", re.DOTALL)


def parse_embedded_json(html: str) -> list[Any]:
    """Parse every JSON script block into Python objects.

    Modern threads.net ships its data in ``type=\"application/json\"`` and
    ``data-sjs`` blocks — both are valid JSON, so every ``<script>`` block
    whose content parses as JSON is included. Malformed blocks are skipped.
    """
    blobs: list[Any] = []
    if not html:
        return blobs
    for match in _SCRIPT_RE.finditer(html):
        raw = match.group(1).strip()
        if not raw:
            continue
        if not raw.startswith(("{", "[")):
            continue
        try:
            blobs.append(json.loads(raw))
        except (json.JSONDecodeError, ValueError):
            continue
    return blobs


def deep_find(
    obj: Any, predicate: Callable[[Any], bool], _seen: set[int] | None = None
) -> list[Any]:
    """Return all values in *obj* matching *predicate* (recursive)."""
    results: list[Any] = []
    seen = _seen if _seen is not None else set()
    ident = id(obj)
    if ident in seen:
        return results
    seen.add(ident)

    if predicate(obj):
        results.append(obj)

    if isinstance(obj, dict):
        for value in obj.values():
            results.extend(deep_find(value, predicate, seen))
    elif isinstance(obj, list):
        for value in obj:
            results.extend(deep_find(value, predicate, seen))
    return results


def deep_find_first(obj: Any, predicate: Callable[[Any], bool]) -> Any | None:
    """Return the first value in *obj* matching *predicate* (recursive)."""
    found = deep_find(obj, predicate)
    return found[0] if found else None


def _dig(obj: Any, *keys: str) -> Any:
    """Dig through nested dicts, returning None on any miss."""
    current = obj
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def parse_threads_profile(html: str, username: str) -> dict[str, Any]:
    """Parse a threads.net/@username profile page."""
    result: dict[str, Any] = {
        "username": username,
        "url": f"https://www.threads.net/@{username}",
    }
    blobs = parse_embedded_json(html)

    def _is_user(node: Any) -> bool:
        return (
            isinstance(node, dict)
            and node.get("username") == username
            and isinstance(node.get("id"), str)
        )

    user = deep_find_first(blobs, _is_user)
    if user:
        result["id"] = user.get("id", "")
        result["name"] = user.get("full_name") or user.get("name") or ""
        result["bio"] = user.get("biography") or ""
        for key in ("followers", "following", "posts"):
            if key in user:
                result[f"{key}_count"] = user[key]
        profile_pic = _dig(user, "profile_pic_url") or _dig(user, "avatar")
        if profile_pic:
            result["profile_pic_url"] = profile_pic
    return result


def _thread_caption_text(node: dict[str, Any]) -> str:
    """Pull the post text from a thread node's ``caption`` payload.

    Modern threads.net ships ``caption`` as a dict (``{\"text\": \"...\"}``);
    older fixtures carry a bare string or a top-level ``text`` key.
    """
    caption = node.get("caption")
    if isinstance(caption, dict):
        return str(caption.get("text") or "")
    if isinstance(caption, str):
        return caption
    return str(node.get("text") or "")


def parse_threads_posts(html: str, username: str, limit: int = 25) -> list[dict[str, Any]]:
    """Parse thread items from a threads.net profile page."""
    posts: list[dict[str, Any]] = []
    seen: set[str] = set()
    blobs = parse_embedded_json(html)

    def _is_thread(node: Any) -> bool:
        if not isinstance(node, dict):
            return False
        node_id = node.get("pk") or node.get("id")
        if not isinstance(node_id, str) or not node_id:
            return False
        caption = node.get("caption")
        has_text = (
            isinstance(node.get("text"), str)
            or isinstance(caption, str)
            or (isinstance(caption, dict) and isinstance(caption.get("text"), str))
        )
        return has_text and ("created_at" in node or "taken_at" in node)

    for node in deep_find(blobs, _is_thread):
        thread_id = str(node.get("pk") or node.get("id", ""))
        if thread_id in seen:
            continue
        seen.add(thread_id)
        code = node.get("code")
        if isinstance(code, str) and code:
            url = f"https://www.threads.net/@{username}/post/{code}"
        else:
            url = f"https://www.threads.net/@{username}/post/{thread_id}"
        app_info = node.get("text_post_app_info") or {}
        if not isinstance(app_info, dict):
            app_info = {}
        posts.append(
            {
                "id": thread_id,
                "code": code if isinstance(code, str) else "",
                "url": url,
                "text": _thread_caption_text(node),
                "created_at": node.get("taken_at") or node.get("created_at", 0),
                "like_count": node.get("like_count", 0) or node.get("likes", 0),
                "reply_count": (
                    node.get("reply_count")
                    or node.get("replies")
                    or app_info.get("direct_reply_count")
                    or 0
                ),
                "repost_count": app_info.get("repost_count") or app_info.get("reshare_count") or 0,
                "media_urls": node.get("media_urls") or node.get("image_versions", []),
            }
        )
        if len(posts) >= limit:
            break
    return posts
