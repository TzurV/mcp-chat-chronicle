"""FTS5 search and conversation detail helpers."""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class SearchResult:
    conversation_id: int
    provider: str
    title: str | None
    updated_at: str | None
    url: str | None
    origin_path: str | None
    resume_hint: str | None
    snippet: str
    rank: float


@dataclass(frozen=True)
class RecentConversation:
    conversation_id: int
    provider: str
    title: str | None
    last_activity_at: str | None
    url: str | None
    origin_path: str | None
    resume_hint: str | None


@dataclass(frozen=True)
class MessageDetail:
    role: str | None
    created_at: str | None
    body: str
    seq: int | None


@dataclass(frozen=True)
class ConversationDetail:
    conversation_id: int
    provider: str
    title: str | None
    created_at: str | None
    updated_at: str | None
    url: str | None
    origin_path: str | None
    resume_hint: str | None
    messages: list[MessageDetail]


_MAX_LIMIT = 100
_SNIPPET_LENGTH = 180
_FTS_KEYWORDS = {"AND", "OR", "NOT", "NEAR"}
_BROAD_SEARCH_HINT_STOP_TERMS = {"you", "are", "the", "a", "an", "to", "of", "in", "for"}
_ADVANCED_FTS_KEYWORDS = {"AND", "OR", "NOT", "NEAR"}


def search_conversations(
    conn: sqlite3.Connection,
    query: str,
    *,
    provider: str | None = None,
    since: str | None = None,
    until: str | None = None,
    tag: str | None = None,
    limit: int = 10,
    phrase: bool = False,
) -> list[SearchResult]:
    """Return ranked FTS5 matches from the normalized archive."""
    normalized_query = query.strip()
    if not normalized_query:
        raise ValueError("Search query cannot be empty.")
    if limit < 1 or limit > _MAX_LIMIT:
        raise ValueError(f"Limit must be between 1 and {_MAX_LIMIT}.")

    normalized_since = _normalize_date_filter(since, end_of_day=False)
    normalized_until = _normalize_date_filter(until, end_of_day=True)
    if phrase:
        return _search_phrase_conversations(
            conn,
            normalized_query,
            provider=provider,
            since=normalized_since,
            until=normalized_until,
            tag=tag,
            limit=limit,
        )

    match_query = _build_broad_match_query(normalized_query)
    if match_query is None:
        # The query is pure punctuation/control syntax with no searchable
        # terms. Treat this as a friendly no-results case rather than passing
        # syntax through to FTS5, which would raise a parser error.
        return []

    clauses = ["chat_fts MATCH ?"]
    params: list[object] = [match_query]
    if provider:
        clauses.append("c.provider = ?")
        params.append(provider)
    if normalized_since:
        clauses.append("coalesce(c.updated_at, c.created_at, '') >= ?")
        params.append(normalized_since)
    if normalized_until:
        clauses.append("coalesce(c.updated_at, c.created_at, '') <= ?")
        params.append(normalized_until)
    if tag:
        clauses.append(
            """
            (
                EXISTS (
                    SELECT 1
                    FROM enrichments AS e_tag
                    WHERE e_tag.conversation_id = c.id
                      AND coalesce(e_tag.tags_json, '') LIKE ?
                )
                OR EXISTS (
                    SELECT 1
                    FROM knowledge_items AS k_tag
                    WHERE k_tag.conversation_id = c.id
                      AND coalesce(k_tag.tags_json, '') LIKE ?
                )
            )
            """
        )
        tag_pattern = f"%{tag}%"
        params.extend([tag_pattern, tag_pattern])
    params.append(limit)

    rows = conn.execute(
        f"""
        SELECT
            c.id AS conversation_id,
            c.provider AS provider,
            c.title AS title,
            coalesce(c.updated_at, c.created_at) AS updated_at,
            c.url AS url,
            c.origin_path AS origin_path,
            c.resume_hint AS resume_hint,
            snippet(chat_fts, 3, '[', ']', ' ... ', 16) AS sqlite_snippet,
            bm25(chat_fts) AS rank
        FROM chat_fts
        JOIN conversations AS c ON c.id = chat_fts.rowid
        WHERE {" AND ".join(clauses)}
        ORDER BY rank ASC, c.id ASC
        LIMIT ?
        """,
        params,
    ).fetchall()

    terms = _query_terms(normalized_query)
    results: list[SearchResult] = []
    for row in rows:
        conversation_id = int(row["conversation_id"])
        snippet = _coerce_sqlite_snippet(row["sqlite_snippet"], terms)
        if snippet is None:
            snippet = _fallback_snippet(conn, conversation_id, terms)
        results.append(
            SearchResult(
                conversation_id=conversation_id,
                provider=row["provider"],
                title=row["title"],
                updated_at=row["updated_at"],
                url=row["url"],
                origin_path=row["origin_path"],
                resume_hint=row["resume_hint"],
                snippet=snippet,
                rank=float(row["rank"]),
            )
        )
    return results


def should_show_broad_search_hint(query: str, *, phrase: bool = False) -> bool:
    """Return whether a broad-token query would benefit from phrase-search guidance."""
    if phrase:
        return False
    normalized_query = query.strip()
    if not normalized_query:
        return False
    if _looks_like_advanced_fts_query(normalized_query):
        return False
    terms = [term.lower() for term in re.findall(r"[\w]+", normalized_query, flags=re.UNICODE)]
    return len(terms) > 1 and bool(_BROAD_SEARCH_HINT_STOP_TERMS.intersection(terms))


def list_recent_conversations(
    conn: sqlite3.Connection,
    *,
    provider: str | None = None,
    since: str | None = None,
    until: str | None = None,
    limit: int = 10,
) -> list[RecentConversation]:
    """Return conversations sorted by most recent activity."""
    if limit < 1 or limit > _MAX_LIMIT:
        raise ValueError(f"Limit must be between 1 and {_MAX_LIMIT}.")

    normalized_since = _normalize_date_filter(since, end_of_day=False)
    normalized_until = _normalize_date_filter(until, end_of_day=True)

    clauses = ["coalesce(c.updated_at, c.created_at) IS NOT NULL"]
    params: list[object] = []
    if provider:
        clauses.append("c.provider = ?")
        params.append(provider)
    if normalized_since:
        clauses.append("coalesce(c.updated_at, c.created_at, '') >= ?")
        params.append(normalized_since)
    if normalized_until:
        clauses.append("coalesce(c.updated_at, c.created_at, '') <= ?")
        params.append(normalized_until)
    params.append(limit)

    rows = conn.execute(
        f"""
        SELECT
            c.id AS conversation_id,
            c.provider AS provider,
            c.title AS title,
            coalesce(c.updated_at, c.created_at) AS last_activity_at,
            c.url AS url,
            c.origin_path AS origin_path,
            c.resume_hint AS resume_hint
        FROM conversations AS c
        WHERE {" AND ".join(clauses)}
        ORDER BY last_activity_at DESC, c.id DESC
        LIMIT ?
        """,
        params,
    ).fetchall()

    return [
        RecentConversation(
            conversation_id=int(row["conversation_id"]),
            provider=row["provider"],
            title=row["title"],
            last_activity_at=row["last_activity_at"],
            url=row["url"],
            origin_path=row["origin_path"],
            resume_hint=row["resume_hint"],
        )
        for row in rows
    ]


def get_conversation_detail(
    conn: sqlite3.Connection,
    conversation_id: int,
) -> ConversationDetail | None:
    """Return a conversation plus ordered transcript messages."""
    row = conn.execute(
        """
        SELECT
            id AS conversation_id,
            provider,
            title,
            created_at,
            updated_at,
            url,
            origin_path,
            resume_hint
        FROM conversations
        WHERE id = ?
        """,
        (conversation_id,),
    ).fetchone()
    if row is None:
        return None

    message_rows = conn.execute(
        """
        SELECT role, created_at, body, seq
        FROM messages
        WHERE conversation_id = ?
        ORDER BY seq ASC, id ASC
        """,
        (conversation_id,),
    ).fetchall()
    messages = [
        MessageDetail(
            role=message["role"],
            created_at=message["created_at"],
            body=message["body"] or "",
            seq=message["seq"],
        )
        for message in message_rows
    ]
    return ConversationDetail(
        conversation_id=int(row["conversation_id"]),
        provider=row["provider"],
        title=row["title"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        url=row["url"],
        origin_path=row["origin_path"],
        resume_hint=row["resume_hint"],
        messages=messages,
    )


def _search_phrase_conversations(
    conn: sqlite3.Connection,
    query: str,
    *,
    provider: str | None,
    since: str | None,
    until: str | None,
    tag: str | None,
    limit: int,
) -> list[SearchResult]:
    clauses = [
        """
        (
            instr(lower(coalesce(c.title, '')), lower(?)) > 0
            OR EXISTS (
                SELECT 1
                FROM messages AS m_phrase
                WHERE m_phrase.conversation_id = c.id
                  AND instr(lower(coalesce(m_phrase.body, '')), lower(?)) > 0
            )
            OR EXISTS (
                SELECT 1
                FROM projects AS p_phrase
                WHERE p_phrase.id = c.project_id
                  AND instr(lower(coalesce(p_phrase.name, '')), lower(?)) > 0
            )
        )
        """
    ]
    where_params: list[object] = [query, query, query]
    if provider:
        clauses.append("c.provider = ?")
        where_params.append(provider)
    if since:
        clauses.append("coalesce(c.updated_at, c.created_at, '') >= ?")
        where_params.append(since)
    if until:
        clauses.append("coalesce(c.updated_at, c.created_at, '') <= ?")
        where_params.append(until)
    if tag:
        clauses.append(
            """
            (
                EXISTS (
                    SELECT 1
                    FROM enrichments AS e_tag
                    WHERE e_tag.conversation_id = c.id
                      AND coalesce(e_tag.tags_json, '') LIKE ?
                )
                OR EXISTS (
                    SELECT 1
                    FROM knowledge_items AS k_tag
                    WHERE k_tag.conversation_id = c.id
                      AND coalesce(k_tag.tags_json, '') LIKE ?
                )
            )
            """
        )
        tag_pattern = f"%{tag}%"
        where_params.extend([tag_pattern, tag_pattern])
    params: list[object] = [query, *where_params, limit]

    rows = conn.execute(
        f"""
        SELECT
            c.id AS conversation_id,
            c.provider AS provider,
            c.title AS title,
            coalesce(c.updated_at, c.created_at) AS updated_at,
            c.url AS url,
            c.origin_path AS origin_path,
            c.resume_hint AS resume_hint,
            CASE
                WHEN instr(lower(coalesce(c.title, '')), lower(?)) > 0 THEN 0.0
                ELSE 1.0
            END AS rank
        FROM conversations AS c
        WHERE {" AND ".join(clauses)}
        ORDER BY rank ASC, updated_at DESC, c.id DESC
        LIMIT ?
        """,
        params,
    ).fetchall()

    return [
        SearchResult(
            conversation_id=int(row["conversation_id"]),
            provider=row["provider"],
            title=row["title"],
            updated_at=row["updated_at"],
            url=row["url"],
            origin_path=row["origin_path"],
            resume_hint=row["resume_hint"],
            snippet=_fallback_snippet(conn, int(row["conversation_id"]), [query.lower()]),
            rank=float(row["rank"]),
        )
        for row in rows
    ]


def _normalize_date_filter(value: str | None, *, end_of_day: bool) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        return None
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", stripped):
        date.fromisoformat(stripped)
        suffix = "T23:59:59.999999Z" if end_of_day else "T00:00:00.000000Z"
        return f"{stripped}{suffix}"

    try:
        datetime.fromisoformat(stripped.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"Invalid date filter: {value}") from exc
    return stripped


def _build_broad_match_query(query: str) -> str | None:
    """Build a safe FTS5 ``MATCH`` expression from raw user text.

    Default broad search treats the query as plain text, not FTS5 syntax.
    Reserved characters such as ``-`` (column filter / ``NOT``), ``:`` (column
    filter), ``()`` (grouping), ``*`` (prefix), and ``"`` (phrase) otherwise
    crash the parser with ``no such column`` or ``syntax error`` when they
    appear in ordinary input like ``scan-local`` or ``C:\\Users\\tzurv``.

    Each searchable term is extracted and emitted as a double-quoted FTS5
    string literal, so a term is never interpreted as an operator or column
    reference. Terms are joined with spaces, giving FTS5's implicit-AND broad
    match. Hyphenated words such as ``scan-local`` split into independent
    ``scan`` and ``local`` terms; exact hyphen matching remains the job of
    ``--phrase``. Returns ``None`` when the query has no searchable terms.
    """
    terms = re.findall(r"[\w]+", query, flags=re.UNICODE)
    if not terms:
        return None
    # Double up any embedded quotes to keep each literal well-formed. The
    # ``\w`` token class cannot contain a double quote, so this is defensive
    # rather than reachable, and it keeps the escaping contract explicit.
    quoted = [f'"{term.replace(chr(34), chr(34) * 2)}"' for term in terms]
    return " ".join(quoted)


def _query_terms(query: str) -> list[str]:
    terms: list[str] = []
    for token in re.findall(r"[\w]+", query, flags=re.UNICODE):
        if token.upper() in _FTS_KEYWORDS:
            continue
        if token.isdigit() and len(token) < 2:
            continue
        terms.append(token.lower())
    return terms


def _looks_like_advanced_fts_query(query: str) -> bool:
    if '"' in query or "(" in query or ")" in query or ":" in query or "*" in query:
        return True
    tokens = re.findall(r"[\w]+", query, flags=re.UNICODE)
    return any(token.upper() in _ADVANCED_FTS_KEYWORDS for token in tokens)


def _coerce_sqlite_snippet(value: object, terms: list[str]) -> str | None:
    if not isinstance(value, str):
        return None
    snippet = _compact_whitespace(value)
    if not snippet or snippet in {"...", "[...]"}:
        return None
    if terms and not any(term in snippet.lower() for term in terms):
        return None
    if not re.search(r"\w", snippet):
        return None
    return snippet


def _fallback_snippet(
    conn: sqlite3.Connection,
    conversation_id: int,
    terms: list[str],
) -> str:
    row = conn.execute(
        """
        SELECT
            c.title AS title,
            e.summary AS summary,
            e.tags_json AS enrichment_tags,
            (
                SELECT group_concat(m.body, char(10))
                FROM messages AS m
                WHERE m.conversation_id = c.id
                ORDER BY m.seq
            ) AS message_body,
            (
                SELECT group_concat(
                    coalesce(k.statement, '') || ' ' || coalesce(k.context, ''),
                    char(10)
                )
                FROM knowledge_items AS k
                WHERE k.conversation_id = c.id
            ) AS knowledge_body,
            (
                SELECT group_concat(coalesce(k.tags_json, ''), ' ')
                FROM knowledge_items AS k
                WHERE k.conversation_id = c.id
            ) AS knowledge_tags,
            p.name AS project_name
        FROM conversations AS c
        LEFT JOIN enrichments AS e ON e.conversation_id = c.id
        LEFT JOIN projects AS p ON p.id = c.project_id
        WHERE c.id = ?
        """,
        (conversation_id,),
    ).fetchone()
    if row is None:
        return ""

    corpus = "\n".join(
        part
        for part in (
            row["title"],
            row["summary"],
            row["enrichment_tags"],
            row["message_body"],
            row["knowledge_body"],
            row["knowledge_tags"],
            row["project_name"],
        )
        if part
    )
    normalized = _compact_whitespace(corpus)
    if not normalized:
        return "(no text available)"

    lower = normalized.lower()
    match_at = -1
    for term in terms:
        match_at = lower.find(term)
        if match_at >= 0:
            break
    if match_at < 0:
        return _truncate(normalized, _SNIPPET_LENGTH)

    start = max(0, match_at - 60)
    end = min(len(normalized), match_at + _SNIPPET_LENGTH - 60)
    snippet = normalized[start:end].strip()
    if start > 0:
        snippet = f"... {snippet}"
    if end < len(normalized):
        snippet = f"{snippet} ..."
    return snippet


def _compact_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _truncate(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value
    return f"{value[: max_length - 4].rstrip()} ..."
