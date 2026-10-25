// Keeps credentials out of everything the probe saves, prints or throws. Mojeek takes its key in the
// request URL (`api_key=`), so a URL, an error message or a fetch failure can all carry it.

const PARAM =
  /([?&;]|\\u0026|\\x26|%26)(api_key|apikey|key|access_token|token)(=|%3D)[^&\s"'\\]*/gi;
const BEARER = /\b(Bearer)\s+[A-Za-z0-9._~+/=-]{8,}/gi;
const PPLX = /\bpplx-[A-Za-z0-9]{8,}/g;

/** Secret values read from the environment this run; any of them found in a string is replaced. */
const known = new Set<string>();

export function registerSecret(value: string | undefined): void {
  if (value !== undefined && value.length >= 6) known.add(value);
}

export function redact(text: string): string {
  let out = text.replace(
    PARAM,
    (_m, sep: string, name: string, eq: string) => `${sep}${name}${eq}REDACTED`,
  );
  out = out.replace(BEARER, "$1 REDACTED").replace(PPLX, "pplx-REDACTED");
  for (const secret of known) {
    out = out.split(secret).join("REDACTED");
    out = out.split(encodeURIComponent(secret)).join("REDACTED");
  }
  return out;
}

/** The only way the probe logs: every line passes through redact(). */
export function log(line: string): void {
  console.log(redact(line));
}
