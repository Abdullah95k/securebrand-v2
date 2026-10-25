"""The one URL normaliser (ADR-0036; Q9), the twin of packages/contracts/src/keys/url.ts step by
step; fixtures/contracts/golden/urls.json holds both to it. The steps are listed in
docs/contracts/VERSIONING.md."""

import re

from listening_contracts._text import lower_case, nfc, require_str, sha256_hex
from listening_contracts.errors import ContractError

_RFC3986 = re.compile(r"(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?", re.DOTALL)
_C0_AND_SPACE = "".join(chr(c) for c in range(0x21))
_UNRESERVED = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~")
_SUB_DELIMS = "!$&'()*+,;="
_PATH_LITERALS = frozenset(_SUB_DELIMS + ":@/")
_QUERY_LITERALS = frozenset(_SUB_DELIMS + ":@/?")
_HEX = re.compile(r"[0-9A-Fa-f]{2}")
_DEFAULT_PORTS = {"http": 80, "https": 443}

type _Parts = tuple[str | None, str | None, str, str | None]  # scheme, authority, path, query


def _parse(s: str) -> _Parts:
    m = _RFC3986.fullmatch(s)
    if m is None:
        raise ContractError("bad_url", s)
    return m.group(2), m.group(4), m.group(5) or "", m.group(7)


def _cleanup(s: str) -> str:
    return re.sub(r"[\t\n\r]", "", s).strip(_C0_AND_SPACE)


def remove_dot_segments(path: str) -> str:
    """RFC 3986 §5.2.4."""
    inp = path
    out: list[str] = []
    while inp:
        if inp.startswith("../"):
            inp = inp[3:]
        elif inp.startswith("./"):
            inp = inp[2:]
        elif inp.startswith("/./"):
            inp = "/" + inp[3:]
        elif inp == "/.":
            inp = "/"
        elif inp.startswith("/../"):
            inp = "/" + inp[4:]
            if out:
                out.pop()
        elif inp == "/..":
            inp = "/"
            if out:
                out.pop()
        elif inp in (".", ".."):
            inp = ""
        else:
            nxt = inp.find("/", 1 if inp.startswith("/") else 0)
            segment = inp if nxt < 0 else inp[:nxt]
            out.append(segment)
            inp = inp[len(segment) :]
    return "".join(out)


def _resolve(ref: _Parts, base: _Parts) -> _Parts:
    """RFC 3986 §5.2.2 (strict) and §5.2.3."""
    r_scheme, r_auth, r_path, r_query = ref
    b_scheme, b_auth, b_path, b_query = base
    if r_scheme is not None:
        return r_scheme, r_auth, remove_dot_segments(r_path), r_query
    if r_auth is not None:
        return b_scheme, r_auth, remove_dot_segments(r_path), r_query
    if r_path == "":
        return b_scheme, b_auth, b_path, r_query if r_query is not None else b_query
    if r_path.startswith("/"):
        path = remove_dot_segments(r_path)
    elif b_auth is not None and b_path == "":
        path = remove_dot_segments("/" + r_path)
    else:
        path = remove_dot_segments(b_path[: b_path.rfind("/") + 1] + r_path)
    return b_scheme, b_auth, path, r_query


def _escape(byte: int) -> str:
    return f"%{byte:02X}"


def _decode_run(data: bytes) -> str | None:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _is_escape(chars: str, i: int) -> bool:
    return chars[i] == "%" and _HEX.fullmatch(chars[i + 1 : i + 3]) is not None


def _normalise_percent(s: str, literals: frozenset[str]) -> str:
    """Percent-encoding in one form: unreserved escapes decoded, other ASCII escapes kept with
    upper-case hex, escaped UTF-8 decoded, text between kept escapes taken in NFC and every
    character outside the literal set encoded as UTF-8 with upper-case hex."""
    parts: list[tuple[str, str]] = []  # ("text" | "escape", value)
    text: list[str] = []

    def flush() -> None:
        if text:
            parts.append(("text", "".join(text)))
            text.clear()

    i = 0
    while i < len(s):
        if _is_escape(s, i):
            data: list[int] = []
            while i < len(s) and _is_escape(s, i):
                data.append(int(s[i + 1 : i + 3], 16))
                i += 3
            j = 0
            while j < len(data):
                b = data[j]
                if b < 0x80:
                    ch = chr(b)
                    if ch in _UNRESERVED:
                        text.append(ch)
                    else:
                        flush()
                        parts.append(("escape", _escape(b)))
                    j += 1
                    continue
                k = j
                while k < len(data) and data[k] >= 0x80:
                    k += 1
                decoded = _decode_run(bytes(data[j:k]))
                if decoded is not None:
                    text.append(decoded)
                else:
                    flush()
                    parts.extend(("escape", _escape(byte)) for byte in data[j:k])
                j = k
            continue
        if s[i] == "%":
            flush()
            parts.append(("escape", "%25"))
        else:
            text.append(s[i])
        i += 1
    flush()
    out: list[str] = []
    for kind, value in parts:
        if kind == "escape":
            out.append(value)
            continue
        for ch in nfc(value):
            if ch in _UNRESERVED or ch in literals:
                out.append(ch)
            else:
                out.extend(_escape(byte) for byte in ch.encode("utf-8"))
    return "".join(out)


def _normalise_host(raw: str) -> str:
    if raw.startswith("["):
        v6 = raw.lower()
        if re.fullmatch(r"\[[0-9a-f:.]+\]", v6) is None or ":" not in v6:
            raise ContractError("bad_host", raw)
        return v6
    host = raw
    if "%" in host:
        data: list[int] = []
        i = 0
        while i < len(host):
            if host[i] == "%" and _HEX.fullmatch(host[i + 1 : i + 3]):
                data.append(int(host[i + 1 : i + 3], 16))
                i += 3
                continue
            if ord(host[i]) >= 0x80:
                raise ContractError("bad_host", raw)
            data.append(ord(host[i]))
            i += 1
        decoded = _decode_run(bytes(data))
        if decoded is None:
            raise ContractError("bad_host", raw)
        host = decoded
    host = nfc(lower_case(nfc(host)))
    labels = host.split(".")
    ascii_labels: list[str] = []
    for i, label in enumerate(labels):
        if label == "":
            if i == len(labels) - 1 and i > 0:
                ascii_labels.append("")
                continue
            raise ContractError("bad_host", f"empty label in {raw}")
        if all(ord(c) < 0x80 for c in label):
            ascii_labels.append(label)
        else:
            ascii_labels.append("xn--" + label.encode("punycode").decode("ascii"))
    out = ".".join(ascii_labels)
    if re.fullmatch(r"[a-z0-9._-]+", out) is None:
        raise ContractError("bad_host", raw)
    return out


def _is_tracking(name: str) -> bool:
    return name.startswith("utm_") or name in ("fbclid", "gclid")


def _normalise_query(query: str) -> str:
    params: list[tuple[str, str | None]] = []
    for piece in query.split("&"):
        if piece == "":
            continue
        eq = piece.find("=")
        name = _normalise_percent(piece if eq < 0 else piece[:eq], _QUERY_LITERALS)
        value = None if eq < 0 else _normalise_percent(piece[eq + 1 :], _QUERY_LITERALS)
        if not _is_tracking(name):
            params.append((name, value))
    params.sort(key=lambda p: (p[0], p[1] is not None, p[1] or ""))
    return "&".join(name if value is None else f"{name}={value}" for name, value in params)


def normalise_url(url: str, base: str | None = None) -> str:
    ref = _parse(_cleanup(require_str(url, "url")))
    if ref[0] is not None:
        target = (ref[0], ref[1], remove_dot_segments(ref[2]), ref[3])
    else:
        if base is None:
            raise ContractError("bad_url", f"{url} is relative and has no base")
        b = _parse(_cleanup(require_str(base, "base")))
        if b[0] is None:
            raise ContractError("bad_url", f"base {base} is not absolute")
        target = _resolve(ref, b)
    scheme = (target[0] or "").lower()
    if scheme not in ("http", "https"):
        raise ContractError("bad_scheme", url)
    authority = target[1]
    if not authority:
        raise ContractError("bad_host", f"{url} has no host")
    if "@" in authority:
        raise ContractError("bad_url", f"{url} carries credentials")
    host_raw = authority
    port: str | None = None
    if authority.startswith("["):
        close = authority.find("]")
        if close < 0:
            raise ContractError("bad_host", url)
        host_raw = authority[: close + 1]
        rest = authority[close + 1 :]
        if rest and not rest.startswith(":"):
            raise ContractError("bad_host", url)
        port = rest[1:] if rest else None
    else:
        colon = authority.rfind(":")
        if colon >= 0:
            host_raw = authority[:colon]
            port = authority[colon + 1 :]
    if host_raw == "":
        raise ContractError("bad_host", f"{url} has no host")
    host = _normalise_host(host_raw)
    port_part = ""
    if port:
        if re.fullmatch(r"[0-9]+", port) is None:
            raise ContractError("bad_port", url)
        n = int(port)
        if n > 65535:
            raise ContractError("bad_port", url)
        if n != _DEFAULT_PORTS[scheme]:
            port_part = f":{n}"
    path = remove_dot_segments(_normalise_percent(target[2], _PATH_LITERALS)) or "/"
    query = "" if target[3] is None else _normalise_query(target[3])
    return f"{scheme}://{host}{port_part}{path}{'?' + query if query else ''}"


def url_hash(url: str, base: str | None = None) -> str:
    """url_hash = hex SHA-256 of the normalised URL's UTF-8 (ADR-0036 RN-10)."""
    return sha256_hex(normalise_url(url, base))


def url_key(url: str, base: str | None = None) -> str:
    return f"news:url:{url_hash(url, base)}"


def canonical_url_hash(canonical_url: str) -> str:
    """The same function over the canonical URL, bare hex (ADR-0036, ADR-0037)."""
    return url_hash(canonical_url)


def article_key(canonical_url: str) -> str:
    return f"news:article:{canonical_url_hash(canonical_url)}"


def web_result_key(canonical_url: str) -> str:
    return f"web:result:{canonical_url_hash(canonical_url)}"
