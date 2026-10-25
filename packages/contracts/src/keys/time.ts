// Timestamps as the keys and ids read them (ADR-0006).
import { ContractError } from "../errors.ts";

const KEY_TIME =
  /^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})(\.[0-9]+)?(Z|[+-][0-9]{2}:?[0-9]{2})$/;
const MESSAGE_TIME =
  /^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})(\.([0-9]{1,3}))?Z$/;

function utcMillis(
  y: number,
  mo: number,
  d: number,
  h: number,
  mi: number,
  s: number,
  t: string,
): number {
  if (y < 1 || mo < 1 || mo > 12 || h > 23 || mi > 59 || s > 59)
    throw new ContractError("bad_time", `${t} names no calendar time`);
  // Date.UTC reads the years 0 to 99 as 1900 to 1999, so the year is set on its own; the years 0001
  // to 9999 are the ones Python's datetime holds, and both languages take the same ones.
  const date = new Date(0);
  date.setUTCFullYear(y, mo - 1, d);
  date.setUTCHours(h, mi, s, 0);
  if (date.getUTCFullYear() !== y || date.getUTCMonth() !== mo - 1 || date.getUTCDate() !== d) {
    throw new ContractError("bad_time", `${t} names no calendar day`);
  }
  return date.getTime();
}

/** A platform time with seconds and an offset, rendered YYYY-MM-DDTHH:MM:SSZ (fractions truncated). */
export function renderKeyTime(t: string): string {
  const m = KEY_TIME.exec(t);
  if (!m) throw new ContractError("bad_time", `${t} is not a time with seconds and an offset`);
  const [y, mo, d, h, mi, s] = m.slice(1, 7).map(Number) as [
    number,
    number,
    number,
    number,
    number,
    number,
  ];
  let ms = utcMillis(y, mo, d, h, mi, s, t);
  const off = m[8] ?? "Z";
  if (off !== "Z") {
    const oh = Number(off.slice(1, 3));
    const om = Number(off.slice(-2));
    if (oh > 23 || om > 59) throw new ContractError("bad_time", t);
    ms -= (off.startsWith("+") ? 1 : -1) * (oh * 3600 + om * 60) * 1000;
  }
  const utc = new Date(ms);
  if (utc.getUTCFullYear() < 1 || utc.getUTCFullYear() > 9999)
    throw new ContractError("bad_time", `${t} falls outside the years 0001 to 9999 in UTC`);
  return utc.toISOString().slice(0, 19) + "Z";
}

/** Milliseconds of a message timestamp: RFC 3339 in UTC with Z and at most three fractional digits. */
export function messageTimeMillis(t: string): number {
  const m = MESSAGE_TIME.exec(t);
  if (!m) throw new ContractError("bad_time", `${t} is not a UTC timestamp`);
  const [y, mo, d, h, mi, s] = m.slice(1, 7).map(Number) as [
    number,
    number,
    number,
    number,
    number,
    number,
  ];
  return utcMillis(y, mo, d, h, mi, s, t) + Number((m[8] ?? "0").padEnd(3, "0"));
}
