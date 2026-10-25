"""The key and id helpers, the twins of packages/contracts/src/keys/: item keys (ADR-0006,
ADR-0007, ADR-0009, ADR-0036, ADR-0038), deterministic ids, author_ref (ADR-0010), content_hash
(ADR-0009), query_key (ADR-0044; Q10), deletion_id (ADR-0035; Q2), candidate keys (ADR-0032) and
raw_ref (ADR-0005).
Every helper takes its inputs as arguments: no environment, clock, network or database."""

import re
from collections.abc import Callable, Mapping, Sequence
from typing import Literal, NamedTuple, TypedDict, cast

from listening_contracts._artefacts import registry
from listening_contracts._text import hmac_sha256_hex, nfc, require_str, sha256_hex
from listening_contracts._time import message_time_millis
from listening_contracts._time import render_key_time as render_key_time
from listening_contracts.canonical_json import canonical_json
from listening_contracts.errors import ContractError
from listening_contracts.patterns import matches
from listening_contracts.vocabulary import (
    CARD_TYPES,
    CONTENT_KINDS,
    DELETION_MODES,
    DELETION_REASONS,
    DELETION_SCOPES,
    PLATFORMS,
)

# Frozen in v1: changing one changes every id derived from it (VERSIONING.md).
NS_ITEMS = "b0eeaa44-bf4b-4c44-b977-bb8c9485f06e"
NS_HITS = "889d9f7d-7cd6-4556-8f5e-3cebf0938434"
NS_CARDS = "68861d52-0265-403a-a35d-493238d31f4b"

# The kind segments each platform keys; an X reply's item kind is comment, its segment post.
_SEGMENTS: dict[str, dict[str, str]] = {
    "facebook": {"post": "post", "comment": "comment"},
    "instagram": {"post": "post", "comment": "comment"},
    "tiktok": {"video": "video", "comment": "comment"},
    "x": {"post": "post", "comment": "post"},
    "linkedin": {"post": "post", "comment": "comment"},
    "telegram": {"post": "post", "comment": "comment"},
    "youtube": {"video": "video", "comment": "comment"},
    "news": {"article": "article", "comment": "comment"},
    "web": {"result": "result"},
}
_HEX_ID_SEGMENTS = frozenset({"news:article", "web:result"})
_ID_CHARS = re.compile(r"[^\x00-\x20]+")


def _uuid5(namespace: str, name: str) -> str:
    import uuid

    if not matches("uuid", namespace):
        raise ContractError("bad_uuid", f"namespace {namespace}")
    return str(uuid.uuid5(uuid.UUID(namespace), name))


def key_segment(platform: str, kind: str) -> str:
    """The kind segment of an item key: the item kind, except an X reply's, which is post."""
    if platform not in PLATFORMS:
        raise ContractError("bad_platform", str(platform))
    if kind not in CONTENT_KINDS:
        raise ContractError("bad_kind", str(kind))
    segment = _SEGMENTS[platform].get(kind)
    if segment is None:
        raise ContractError("bad_kind", f"{platform} keys no {kind}")
    return segment


def idempotency_key(platform: str, kind: str, platform_id: str) -> str:
    segment = key_segment(platform, kind)
    pid = nfc(require_str(platform_id, "platform_id"))
    if _ID_CHARS.fullmatch(pid) is None:
        raise ContractError("bad_platform_id", "empty or holds a space or control character")
    if f"{platform}:{segment}" in _HEX_ID_SEGMENTS and not matches("sha256Hex", pid):
        raise ContractError("bad_platform_id", f"{platform}:{segment} takes 64 lower-case hex")
    return nfc(f"{platform}:{segment}:{pid}")


class ParsedKey(TypedDict):
    platform: str
    kind: str
    platform_id: str


def parse_key(key: str) -> ParsedKey:
    require_str(key, "key")
    parts = key.split(":", 2)
    if len(parts) < 3:
        raise ContractError("bad_key", f"{key} has fewer than three segments")
    platform, kind, pid = parts
    if platform not in PLATFORMS:
        raise ContractError("bad_key", f"unknown platform in {key}")
    if kind not in _SEGMENTS[platform].values():
        raise ContractError("bad_key", f"{platform} keys no {kind}")
    if _ID_CHARS.fullmatch(pid) is None:
        raise ContractError("bad_key", f"{key} has an empty or spaced id")
    if f"{platform}:{kind}" in _HEX_ID_SEGMENTS and not matches("sha256Hex", pid):
        raise ContractError("bad_key", f"{key} needs a 64 lower-case hex id")
    return {"platform": platform, "kind": kind, "platform_id": pid}


_USERNAME = re.compile(r"[A-Za-z][A-Za-z0-9_]*")
_CHAT_ID = re.compile(r"-?[0-9]+")
_DIGITS = re.compile(r"[0-9]+")
_SHORTCODE = re.compile(r"[A-Za-z0-9_-]+")


def telegram_post_id(channel: str, message_id: str) -> str:
    """`<lowercase username>/<message_id>`, or the chat id for a channel without a username."""
    require_str(channel, "channel")
    if _DIGITS.fullmatch(message_id) is None:
        raise ContractError("bad_platform_id", "message id must be digits")
    if _CHAT_ID.fullmatch(channel):
        return f"{channel}/{message_id}"
    if _USERNAME.fullmatch(channel) is None:
        raise ContractError("bad_platform_id", f"channel {channel}")
    return f"{channel.lower()}/{message_id}"


def telegram_comment_id(group_chat_id: str, message_id: str) -> str:
    if _CHAT_ID.fullmatch(group_chat_id) is None:
        raise ContractError("bad_platform_id", "group chat id must be a number")
    if _DIGITS.fullmatch(message_id) is None:
        raise ContractError("bad_platform_id", "message id must be digits")
    return f"{group_chat_id}/{message_id}"


def linkedin_post_id(post_id: str, urn: Literal["activity", "share"]) -> str:
    """The activity or share URN form, chosen by an explicit argument (ADR-0007; LI0 decides)."""
    if _DIGITS.fullmatch(post_id) is None:
        raise ContractError("bad_platform_id", "post id must be digits")
    if urn not in ("activity", "share"):
        raise ContractError("bad_platform_id", f"urn {urn}")
    return f"urn:li:{urn}:{post_id}"


def linkedin_comment_id(post_id: str, comment_id: str, urn: Literal["activity", "share"]) -> str:
    if _DIGITS.fullmatch(comment_id) is None:
        raise ContractError("bad_platform_id", "comment id must be digits")
    return f"urn:li:comment:({linkedin_post_id(post_id, urn)},{comment_id})"


def instagram_shortcode_id(shortcode: str) -> str:
    if _SHORTCODE.fullmatch(shortcode) is None:
        raise ContractError("bad_platform_id", f"shortcode {shortcode}")
    return f"sc:{shortcode}"


def idless_comment_key(platform: str, post_id: str, created_time: str, text: str) -> str:
    """`<platform>:comment:<post id>:<hex sha256 of NFC(created_time + text)>` (ADR-0009)."""
    require_str(post_id, "post_id")
    require_str(text, "text")
    digest = sha256_hex(nfc(render_key_time(require_str(created_time, "created_time")) + text))
    return idempotency_key(platform, "comment", f"{post_id}:{digest}")


class InstagramMapRow(TypedDict):
    shortcode: str
    graph_media_id: str | None
    key: str


class InstagramKey(NamedTuple):
    key: str
    map_row: InstagramMapRow | None


def instagram_post_key(
    route: Literal["graph", "vendor"],
    media_id: str | None,
    shortcode: str | None,
    lookup: Callable[[str], InstagramMapRow | None],
) -> InstagramKey:
    """The Instagram id map rule (ADR-0007): a pure function over a lookup by shortcode, returning
    key and the map row the SDK writes."""
    if shortcode is not None and _SHORTCODE.fullmatch(shortcode) is None:
        raise ContractError("bad_shortcode", shortcode)
    if media_id is not None and _DIGITS.fullmatch(media_id) is None:
        raise ContractError("bad_media_id", media_id)
    if route == "graph":
        if media_id is None:
            raise ContractError("bad_media_id", "a Graph read carries its media id")
        known = None if shortcode is None else lookup(shortcode)
        key = known["key"] if known else f"instagram:post:{media_id}"
        row: InstagramMapRow | None = (
            None
            if shortcode is None
            else {"shortcode": shortcode, "graph_media_id": media_id, "key": key}
        )
        return InstagramKey(key, row)
    if route != "vendor":
        raise ContractError("bad_route", str(route))
    if shortcode is None:
        raise ContractError("bad_shortcode", "a vendor read keys on its shortcode")
    known = lookup(shortcode)
    key = known["key"] if known else f"instagram:post:sc:{shortcode}"
    graph_id = known["graph_media_id"] if known else media_id
    return InstagramKey(key, {"shortcode": shortcode, "graph_media_id": graph_id, "key": key})


def _require_uuid(value: str, what: str) -> str:
    if not matches("uuid", value):
        raise ContractError("bad_uuid", f"{what} {value}")
    return value


def item_id(key: str) -> str:
    """item_id = uuid_v5(ns_items, key), the key taken in its NFC form."""
    k = nfc(require_str(key, "key"))
    parse_key(k)
    return _uuid5(NS_ITEMS, k)


def hit_id(item_id_value: str, client_id: str, keyword_id: str) -> str:
    """uuid_v5(ns_hits, "<item_id>:<client_id>:<keyword_id>") (keyword-matcher §5.3 L77)."""
    name = ":".join(
        (
            _require_uuid(item_id_value, "item_id"),
            _require_uuid(client_id, "client_id"),
            _require_uuid(keyword_id, "keyword_id"),
        )
    )
    return _uuid5(NS_HITS, name)


def card_id(card_type: str, subject_key: str, ref: str) -> str:
    """uuid_v5(ns_cards, "<card_type>:<subject key>:<decision_id or request_id>") (Q11, F-47)."""
    if card_type not in CARD_TYPES:
        raise ContractError("bad_card_type", card_type)
    if not matches("token", subject_key):
        raise ContractError("bad_subject", str(subject_key))
    if not matches("ulid", ref):
        raise ContractError("bad_ulid", f"ref {ref}")
    return _uuid5(NS_CARDS, f"{card_type}:{subject_key}:{ref}")


def analysis_key(item_id_value: str, task: str, model_version: str) -> str:
    """`<item_id>:<task>:<model_version>`; task and model version hold no colon (ADR-0023)."""
    _require_uuid(item_id_value, "item_id")
    if not matches("analysisTask", task):
        raise ContractError("bad_task", str(task))
    if not matches("modelVersion", model_version):
        raise ContractError("bad_model_version", str(model_version))
    return f"{item_id_value}:{task}:{model_version}"


def author_ref(key: bytes, platform: str, author_platform_id: str) -> str:
    """HMAC-SHA256(key, UTF-8(NFC("<platform>:<author platform id>"))) (ADR-0010). The key is an
    argument: Vault holds the real one, and the package never reads a key itself."""
    if not isinstance(key, bytes) or len(key) == 0:  # pyright: ignore[reportUnnecessaryIsInstance] - callers may pass anything
        raise ContractError("bad_key", "the HMAC key is empty")
    if platform not in PLATFORMS:
        raise ContractError("bad_platform", str(platform))
    if require_str(author_platform_id, "author platform id") == "":
        raise ContractError("bad_author_id", "the author platform id is empty")
    return hmac_sha256_hex(key, nfc(f"{platform}:{author_platform_id}"))


def matches_author_ref(
    ref: str, platform: str, author_platform_id: str, keys: Sequence[bytes]
) -> bool:
    """True when the reference matches under any key still covering retained data (ADR-0010)."""
    return any(author_ref(k, platform, author_platform_id) == ref for k in keys)


def content_hash(title: str | None, text: str | None) -> str:
    """ "sha256:" + hex SHA-256 of NFC(title) + U+001F + NFC(text), or of NFC(text) without a title;
    media URLs never enter it (ADR-0009)."""
    body = nfc("" if text is None else require_str(text, "text"))
    if title is not None and require_str(title, "title") != "":
        return "sha256:" + sha256_hex(f"{nfc(title)}\u001f{body}")
    return "sha256:" + sha256_hex(body)


type FoldingProfile = Literal["exact", "folded"]
_TATWEEL = 0x0640
_FOLD = {
    0x0623: 0x0627,
    0x0625: 0x0627,
    0x0622: 0x0627,
    0x0629: 0x0647,
    0x0649: 0x064A,
    0x06A9: 0x0643,
    0x06CC: 0x064A,
}


def _is_tashkeel(cp: int) -> bool:
    return 0x064B <= cp <= 0x065F or cp == 0x0670


def folding_profile(platform: str) -> FoldingProfile:
    if platform not in PLATFORMS:
        raise ContractError("bad_platform", str(platform))
    profiles = cast(dict[str, dict[str, str]], registry("query-folding.json"))["profiles"]
    profile = profiles.get(platform)
    if profile == "exact":
        return "exact"
    if profile == "folded":
        return "folded"
    raise ContractError("bad_registry", f"no profile for {platform}")


def normalise_query_text(profile: FoldingProfile, text: str) -> str:
    lowered = nfc(require_str(text, "form")).lower()
    if profile == "exact":
        return lowered
    return "".join(
        chr(_FOLD.get(ord(ch), ord(ch)))
        for ch in lowered
        if ord(ch) != _TATWEEL and not _is_tashkeel(ord(ch))
    )


def _normalise_list(profile: FoldingProfile, texts: Sequence[str], what: str) -> list[str]:
    out: set[str] = set()
    for text in texts:
        n = normalise_query_text(profile, text)
        if n == "":
            raise ContractError("bad_keyword", f"an empty {what}")
        out.add(n)
    return sorted(out)  # Python orders strings by code point, as the TypeScript helper does


def query_key_with_profile(
    profile: FoldingProfile, forms: Sequence[str], context_terms: Sequence[str]
) -> str:
    if profile not in ("exact", "folded"):
        raise ContractError("bad_profile", str(profile))
    if len(forms) == 0:
        raise ContractError("bad_keyword", "a keyword needs at least one form")
    value = {
        "context_terms": _normalise_list(profile, context_terms, "context term"),
        "forms": _normalise_list(profile, forms, "form"),
    }
    return sha256_hex(canonical_json(value))


def query_key(platform: str, forms: Sequence[str], context_terms: Sequence[str]) -> str:
    """The hash of a keyword's forms and context terms under its platform's profile (ADR-0044)."""
    return query_key_with_profile(folding_profile(platform), forms, context_terms)


def deletion_id(
    reason: str,
    scope: str,
    key: str,
    mode: str,
    signal_at: str,
    target: Mapping[str, str | Sequence[str]],
) -> str:
    """`del:<reason>:<scope>:` + hex SHA-256 of the RFC 8785 JSON of
    {key, mode, signal_day, target},
    every target array sorted (ADR-0035; Q2, decided by the user)."""
    if reason not in DELETION_REASONS:
        raise ContractError("bad_reason", str(reason))
    if scope not in DELETION_SCOPES:
        raise ContractError("bad_scope", str(scope))
    if mode not in DELETION_MODES:
        raise ContractError("bad_mode", str(mode))
    if not matches("sha256Hex" if scope == "author" else "uuid", key):
        raise ContractError(
            "bad_key", f"{scope} scope takes {'an author_ref' if scope == 'author' else 'a UUID'}"
        )
    message_time_millis(require_str(signal_at, "signal_at"))
    sorted_target: dict[str, str | list[str]] = {}
    for name, value in target.items():
        if isinstance(value, str):
            sorted_target[name] = value
        elif isinstance(value, (list, tuple)):
            items = cast(Sequence[object], value)
            sorted_target[name] = sorted(
                require_str(v, f"{name}[{i}]") for i, v in enumerate(items)
            )
        else:
            raise ContractError("bad_target", f"{name} must be a string or an array of strings")
    text = canonical_json(
        {"key": key, "mode": mode, "signal_day": signal_at[:10], "target": sorted_target}
    )
    return f"del:{reason}:{scope}:{sha256_hex(text)}"


_ACCOUNT_PLATFORMS = ("facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube")
_CANDIDATE_VALUE = re.compile(r"[^\x00-\x20:]+")
# A LinkedIn organisation's id is its URN (`urn:li:organization:<n>`), so its value may hold colons.
_CANDIDATE_URN_VALUE = re.compile(r"[^\x00-\x20]+")
_DOMAIN = re.compile(r"[a-z0-9-]+(\.[a-z0-9-]+)+")


def _account_platform(platform: str) -> str:
    if platform not in _ACCOUNT_PLATFORMS:
        raise ContractError("bad_platform", f"{platform} has no account candidates")
    return platform


def _valid_candidate_value(platform: str, value: str) -> bool:
    pattern = _CANDIDATE_URN_VALUE if platform == "linkedin" else _CANDIDATE_VALUE
    return pattern.fullmatch(value) is not None


def candidate_key_from_id(platform: str, platform_id: str) -> str:
    """`<platform>:<platform_id>`; an id keeps its case (ADR-0032)."""
    p = _account_platform(platform)
    if not _valid_candidate_value(p, require_str(platform_id, "id")):
        raise ContractError("bad_candidate", platform_id)
    return f"{p}:{platform_id}"


def candidate_key_from_handle(platform: str, handle: str) -> str:
    """`<platform>:<handle>`, the handle lower case without a leading '@' (ADR-0032)."""
    p = _account_platform(platform)
    h = nfc(re.sub(r"^@", "", require_str(handle, "handle"))).lower()
    if not _valid_candidate_value(p, h):
        raise ContractError("bad_candidate", handle)
    return f"{p}:{h}"


def facebook_group_candidate_key(group_id: str) -> str:
    if _DIGITS.fullmatch(require_str(group_id, "group id")) is None:
        raise ContractError("bad_candidate", group_id)
    return f"facebook:group:{group_id}"


def news_site_candidate_key(registrable_domain: str) -> str:
    """The registrable domain is computed by the caller: the package holds no public-suffix list."""
    d = require_str(registrable_domain, "domain").lower()
    if _DOMAIN.fullmatch(d) is None:
        raise ContractError("bad_candidate", registrable_domain)
    return f"news:site:{d}"


class ParsedCandidateKey(TypedDict):
    platform: str
    form: Literal["account", "group", "site"]
    value: str


def parse_candidate_key(key: str) -> ParsedCandidateKey:
    require_str(key, "candidate_key")
    m = re.fullmatch(r"facebook:group:([0-9]+)", key)
    if m:
        return {"platform": "facebook", "form": "group", "value": m.group(1)}
    m = re.fullmatch(r"news:site:([a-z0-9-]+(\.[a-z0-9-]+)+)", key)
    if m:
        return {"platform": "news", "form": "site", "value": m.group(1)}
    platform, colon, value = key.partition(":")
    if not _valid_candidate_value(_account_platform(platform if colon else ""), value):
        raise ContractError("bad_candidate", key)
    return {"platform": platform, "form": "account", "value": value}


class RawRef(TypedDict):
    route: str
    platform: str
    date: str
    service: str
    batch: int
    line: int


def raw_ref(route: str, platform: str, date: str, service: str, batch: int, line: int) -> str:
    """`raw/<route>/<platform>/<yyyy>/<mm>/<dd>/<service>/<batch>.jsonl.zst#<line>`

    The batch number has six digits (ADR-0039)."""
    if isinstance(batch, bool) or not 0 <= batch <= 999_999:
        raise ContractError("bad_raw_ref", f"batch {batch}")
    if isinstance(line, bool) or line < 0:
        raise ContractError("bad_raw_ref", f"line {line}")
    if not matches("date", date):
        raise ContractError("bad_raw_ref", f"date {date}")
    out = f"raw/{route}/{platform}/{date.replace('-', '/')}/{service}/{batch:06d}.jsonl.zst#{line}"
    if not matches("rawRef", out):
        raise ContractError("bad_raw_ref", out)
    return out


def parse_raw_ref(value: str) -> RawRef:
    if not matches("rawRef", value):
        raise ContractError("bad_raw_ref", str(value))
    _raw, route, platform, y, mo, d, service, rest = value.split("/")
    file, _hash, line = rest.partition("#")
    return {
        "route": route,
        "platform": platform,
        "date": f"{y}-{mo}-{d}",
        "service": service,
        "batch": int(file[:6]),
        "line": int(line),
    }
