// The Instagram id map rule (ADR-0007): a pure function over a lookup by shortcode. It returns the key
// and the map row the SDK writes, since only the key helper writes the map.
import { ContractError } from "../errors.ts";

export interface InstagramMapRow {
  shortcode: string;
  graph_media_id: string | null;
  key: string;
}

export interface InstagramRead {
  route: "graph" | "vendor";
  media_id: string | null;
  shortcode: string | null;
}

const SHORTCODE = /^[A-Za-z0-9_-]+$/;
const MEDIA_ID = /^[0-9]+$/;

export function instagramPostKey(
  read: InstagramRead,
  lookup: (shortcode: string) => InstagramMapRow | null,
): { key: string; map_row: InstagramMapRow | null } {
  const { shortcode } = read;
  if (shortcode !== null && !SHORTCODE.test(shortcode))
    throw new ContractError("bad_shortcode", shortcode);
  if (read.media_id !== null && !MEDIA_ID.test(read.media_id))
    throw new ContractError("bad_media_id", read.media_id);
  if (read.route === "graph") {
    if (read.media_id === null)
      throw new ContractError("bad_media_id", "a Graph read carries its media id");
    const known = shortcode === null ? null : lookup(shortcode);
    const key = known ? known.key : `instagram:post:${read.media_id}`;
    return {
      key,
      map_row: shortcode === null ? null : { shortcode, graph_media_id: read.media_id, key },
    };
  }
  if (read.route !== "vendor") throw new ContractError("bad_route", String(read.route));
  if (shortcode === null)
    throw new ContractError("bad_shortcode", "a vendor read keys on its shortcode");
  const known = lookup(shortcode);
  const key = known ? known.key : `instagram:post:sc:${shortcode}`;
  return {
    key,
    map_row: { shortcode, graph_media_id: known?.graph_media_id ?? read.media_id, key },
  };
}
