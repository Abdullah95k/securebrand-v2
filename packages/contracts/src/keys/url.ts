// The one URL normaliser (ADR-0036; Q9) for every news finder, the extractor, the four
// search.results producers and search-hit-router. The steps are listed in docs/contracts/VERSIONING.md;
// the Python twin follows them line by line, and fixtures/contracts/golden/urls.json holds both to them.
import { ContractError } from "../errors.ts";
import { lowerCase, nfc, requireString, sha256Hex } from "./text.ts";

const RFC3986 = /^(([^:/?#]+):)?(\/\/([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?$/s;

interface Parts {
  scheme: string | undefined;
  authority: string | undefined;
  path: string;
  query: string | undefined;
}

function parse(s: string): Parts {
  const m = RFC3986.exec(s);
  if (!m) throw new ContractError("bad_url", s);
  return { scheme: m[2], authority: m[4], path: m[5] ?? "", query: m[7] };
}

function cleanup(s: string): string {
  // eslint-disable-next-line no-control-regex -- C0 controls and spaces are trimmed, as WHATWG URL does
  return s.replace(/[\t\n\r]/g, "").replace(/^[\x00-\x20]+|[\x00-\x20]+$/g, "");
}

// RFC 3986 §5.2.4.
export function removeDotSegments(path: string): string {
  let input = path;
  const output: string[] = [];
  while (input.length > 0) {
    if (input.startsWith("../")) input = input.slice(3);
    else if (input.startsWith("./")) input = input.slice(2);
    else if (input.startsWith("/./")) input = `/${input.slice(3)}`;
    else if (input === "/.") input = "/";
    else if (input.startsWith("/../")) {
      input = `/${input.slice(4)}`;
      output.pop();
    } else if (input === "/..") {
      input = "/";
      output.pop();
    } else if (input === "." || input === "..") input = "";
    else {
      const next = input.indexOf("/", input.startsWith("/") ? 1 : 0);
      const segment = next < 0 ? input : input.slice(0, next);
      output.push(segment);
      input = input.slice(segment.length);
    }
  }
  return output.join("");
}

// RFC 3986 §5.2.2 (strict) and §5.2.3.
function resolve(ref: Parts, base: Parts): Parts {
  if (ref.scheme !== undefined) return { ...ref, path: removeDotSegments(ref.path) };
  if (ref.authority !== undefined) {
    return {
      scheme: base.scheme,
      authority: ref.authority,
      path: removeDotSegments(ref.path),
      query: ref.query,
    };
  }
  if (ref.path === "") {
    return {
      scheme: base.scheme,
      authority: base.authority,
      path: base.path,
      query: ref.query ?? base.query,
    };
  }
  let path: string;
  if (ref.path.startsWith("/")) path = removeDotSegments(ref.path);
  else if (base.authority !== undefined && base.path === "")
    path = removeDotSegments(`/${ref.path}`);
  else path = removeDotSegments(base.path.slice(0, base.path.lastIndexOf("/") + 1) + ref.path);
  return { scheme: base.scheme, authority: base.authority, path, query: ref.query };
}

const UNRESERVED = /^[A-Za-z0-9\-._~]$/;
const SUB_DELIMS = "!$&'()*+,;=";
const PATH_LITERALS = new Set([...SUB_DELIMS, ":", "@", "/"]);
const QUERY_LITERALS = new Set([...SUB_DELIMS, ":", "@", "/", "?"]);
const HEX = /^[0-9A-Fa-f]{2}$/;
const utf8Decoder = new TextDecoder("utf-8", { fatal: true, ignoreBOM: true });
const utf8Encoder = new TextEncoder();
const escape = (byte: number): string => `%${byte.toString(16).toUpperCase().padStart(2, "0")}`;

function decodeRun(bytes: number[]): string | null {
  try {
    return utf8Decoder.decode(new Uint8Array(bytes));
  } catch {
    return null;
  }
}

/**
 * Percent-encoding in one form: unreserved escapes decoded, other ASCII escapes kept with upper-case
 * hex, escaped UTF-8 decoded, text between kept escapes taken in NFC and every character outside the
 * literal set encoded as UTF-8 with upper-case hex.
 */
function normalisePercent(s: string, literals: Set<string>): string {
  const parts: ({ text: string } | { escape: string })[] = [];
  let text = "";
  const flush = (): void => {
    if (text !== "") parts.push({ text });
    text = "";
  };
  const chars = Array.from(s);
  let i = 0;
  while (i < chars.length) {
    const c = chars[i] ?? "";
    if (c === "%" && HEX.test((chars[i + 1] ?? "") + (chars[i + 2] ?? ""))) {
      const bytes: number[] = [];
      while (chars[i] === "%" && HEX.test((chars[i + 1] ?? "") + (chars[i + 2] ?? ""))) {
        bytes.push(parseInt((chars[i + 1] ?? "") + (chars[i + 2] ?? ""), 16));
        i += 3;
      }
      let j = 0;
      while (j < bytes.length) {
        const b = bytes[j] ?? 0;
        if (b < 0x80) {
          const ch = String.fromCharCode(b);
          if (UNRESERVED.test(ch)) text += ch;
          else {
            flush();
            parts.push({ escape: escape(b) });
          }
          j += 1;
          continue;
        }
        let k = j;
        while (k < bytes.length && (bytes[k] ?? 0) >= 0x80) k += 1;
        const run = bytes.slice(j, k);
        const decoded = decodeRun(run);
        if (decoded !== null) text += decoded;
        else {
          flush();
          for (const byte of run) parts.push({ escape: escape(byte) });
        }
        j = k;
      }
      continue;
    }
    if (c === "%") {
      flush();
      parts.push({ escape: "%25" });
    } else text += c;
    i += 1;
  }
  flush();
  let out = "";
  for (const part of parts) {
    if ("escape" in part) {
      out += part.escape;
      continue;
    }
    for (const ch of nfc(part.text)) {
      if (UNRESERVED.test(ch) || literals.has(ch)) out += ch;
      else for (const byte of utf8Encoder.encode(ch)) out += escape(byte);
    }
  }
  return out;
}

// RFC 3492 Punycode, for hosts in their ASCII form.
function punycode(label: string): string {
  const base = 36;
  const tMin = 1;
  const tMax = 26;
  const adapt = (deltaIn: number, points: number, first: boolean): number => {
    let delta = first ? Math.floor(deltaIn / 700) : deltaIn >> 1;
    delta += Math.floor(delta / points);
    let k = 0;
    while (delta > ((base - tMin) * tMax) >> 1) {
      delta = Math.floor(delta / (base - tMin));
      k += base;
    }
    return k + Math.floor(((base - tMin + 1) * delta) / (delta + 38));
  };
  const digit = (d: number): string => String.fromCharCode(d < 26 ? 97 + d : 22 + d);
  const cps = Array.from(label, (c) => c.codePointAt(0) ?? 0);
  const out = cps.filter((c) => c < 0x80).map((c) => String.fromCharCode(c));
  const basic = out.length;
  let handled = basic;
  if (basic > 0) out.push("-");
  let n = 128;
  let delta = 0;
  let bias = 72;
  while (handled < cps.length) {
    const m = Math.min(...cps.filter((c) => c >= n));
    delta += (m - n) * (handled + 1);
    n = m;
    for (const c of cps) {
      if (c < n) delta += 1;
      if (c === n) {
        let q = delta;
        for (let k = base; ; k += base) {
          const t = k <= bias ? tMin : k >= bias + tMax ? tMax : k - bias;
          if (q < t) break;
          out.push(digit(t + ((q - t) % (base - t))));
          q = Math.floor((q - t) / (base - t));
        }
        out.push(digit(q));
        bias = adapt(delta, handled + 1, handled === basic);
        delta = 0;
        handled += 1;
      }
    }
    delta += 1;
    n += 1;
  }
  return out.join("");
}

function normaliseHost(raw: string): string {
  if (raw.startsWith("[")) {
    const v6 = raw.toLowerCase();
    if (!/^\[[0-9a-f:.]+\]$/.test(v6) || !v6.includes(":"))
      throw new ContractError("bad_host", raw);
    return v6;
  }
  let host = raw;
  if (host.includes("%")) {
    const bytes: number[] = [];
    for (let i = 0; i < host.length; i += 1) {
      if (host[i] === "%" && HEX.test(host.slice(i + 1, i + 3))) {
        bytes.push(parseInt(host.slice(i + 1, i + 3), 16));
        i += 2;
      } else if (host.charCodeAt(i) < 0x80) bytes.push(host.charCodeAt(i));
      else throw new ContractError("bad_host", raw);
    }
    const decoded = decodeRun(bytes);
    if (decoded === null) throw new ContractError("bad_host", raw);
    host = decoded;
  }
  host = nfc(lowerCase(nfc(host)));
  const labels = host.split(".");
  const ascii = labels.map((label, i) => {
    if (label === "") {
      if (i === labels.length - 1 && i > 0) return "";
      throw new ContractError("bad_host", `empty label in ${raw}`);
    }
    // eslint-disable-next-line no-control-regex -- an ASCII label is any of the 128 code points
    return /^[\x00-\x7f]*$/.test(label) ? label : `xn--${punycode(label)}`;
  });
  const out = ascii.join(".");
  if (!/^[a-z0-9._-]+$/.test(out)) throw new ContractError("bad_host", raw);
  return out;
}

const DEFAULT_PORTS: Record<string, number> = { http: 80, https: 443 };

function isTracking(name: string): boolean {
  return name.startsWith("utm_") || name === "fbclid" || name === "gclid";
}

function normaliseQuery(query: string): string {
  const params: { name: string; value: string | null }[] = [];
  for (const piece of query.split("&")) {
    if (piece === "") continue;
    const eq = piece.indexOf("=");
    const name = normalisePercent(eq < 0 ? piece : piece.slice(0, eq), QUERY_LITERALS);
    const value = eq < 0 ? null : normalisePercent(piece.slice(eq + 1), QUERY_LITERALS);
    if (!isTracking(name)) params.push({ name, value });
  }
  // Normalised names and values are ASCII, so code unit and code point order agree.
  params.sort((a, b) => {
    if (a.name !== b.name) return a.name < b.name ? -1 : 1;
    if (a.value === b.value) return 0;
    if (a.value === null) return -1;
    if (b.value === null) return 1;
    return a.value < b.value ? -1 : 1;
  });
  return params.map((p) => (p.value === null ? p.name : `${p.name}=${p.value}`)).join("&");
}

export function normaliseUrl(url: string, base?: string): string {
  const input = cleanup(requireString(url, "url"));
  const ref = parse(input);
  let target: Parts;
  if (ref.scheme !== undefined) target = { ...ref, path: removeDotSegments(ref.path) };
  else {
    if (base === undefined)
      throw new ContractError("bad_url", `${url} is relative and has no base`);
    const b = parse(cleanup(requireString(base, "base")));
    if (b.scheme === undefined) throw new ContractError("bad_url", `base ${base} is not absolute`);
    target = resolve(ref, b);
  }
  const scheme = (target.scheme ?? "").toLowerCase();
  if (scheme !== "http" && scheme !== "https") throw new ContractError("bad_scheme", url);
  const authority = target.authority;
  if (authority === undefined || authority === "")
    throw new ContractError("bad_host", `${url} has no host`);
  if (authority.includes("@")) throw new ContractError("bad_url", `${url} carries credentials`);
  let hostRaw = authority;
  let port: string | undefined;
  if (authority.startsWith("[")) {
    const close = authority.indexOf("]");
    if (close < 0) throw new ContractError("bad_host", url);
    hostRaw = authority.slice(0, close + 1);
    const rest = authority.slice(close + 1);
    if (rest !== "" && !rest.startsWith(":")) throw new ContractError("bad_host", url);
    port = rest === "" ? undefined : rest.slice(1);
  } else {
    const colon = authority.lastIndexOf(":");
    if (colon >= 0) {
      hostRaw = authority.slice(0, colon);
      port = authority.slice(colon + 1);
    }
  }
  if (hostRaw === "") throw new ContractError("bad_host", `${url} has no host`);
  const host = normaliseHost(hostRaw);
  let portPart = "";
  if (port !== undefined && port !== "") {
    if (!/^[0-9]+$/.test(port)) throw new ContractError("bad_port", url);
    const n = Number(port);
    if (n > 65535) throw new ContractError("bad_port", url);
    if (n !== DEFAULT_PORTS[scheme]) portPart = `:${n}`;
  }
  const path = removeDotSegments(normalisePercent(target.path, PATH_LITERALS)) || "/";
  const query = target.query === undefined ? "" : normaliseQuery(target.query);
  return `${scheme}://${host}${portPart}${path}${query === "" ? "" : `?${query}`}`;
}

/** url_hash = hex SHA-256 of the normalised URL's UTF-8 (ADR-0036 RN-10). */
export function urlHash(url: string, base?: string): string {
  return sha256Hex(normaliseUrl(url, base));
}

export function urlKey(url: string, base?: string): string {
  return `news:url:${urlHash(url, base)}`;
}

/** canonical_url_hash: the same function over the canonical URL, bare hex (ADR-0036, ADR-0037). */
export function canonicalUrlHash(canonicalUrl: string): string {
  return urlHash(canonicalUrl);
}

export function articleKey(canonicalUrl: string): string {
  return `news:article:${canonicalUrlHash(canonicalUrl)}`;
}

export function webResultKey(canonicalUrl: string): string {
  return `web:result:${canonicalUrlHash(canonicalUrl)}`;
}
