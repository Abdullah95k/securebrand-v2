"""raw.items/v1 fixtures: one rewritten PRD example per producer (A6), a branch fixture per record
kind, invalid fixtures for each rule (A5, A20) and tolerant ones (A32)."""

from datetime import datetime, timedelta
from typing import Any

from common import (
    CLIENT,
    iid,
    invalid,
    key,
    meta,
    prd,
    prov,
    rawref,
    ref,
    tolerant,
    valid,
    with_,
    without,
)

from listening_contracts.keys import (
    candidate_key_from_handle,
    candidate_key_from_id,
    idless_comment_key,
    linkedin_comment_id,
    linkedin_post_id,
    news_site_candidate_key,
    telegram_comment_id,
    telegram_post_id,
)
from listening_contracts.url import article_key, url_key

S = "raw.items/v1"
R_META = "schema, message_id, produced_at and producer stamped by the SDK (ADR-0002)"
R_PROV = "route, vendor, service and fetched_at fold into provenance (ADR-0003)"
R_BATCH = "batch gives way to raw_ref, which names the object and line (ADR-0005)"
R_JOBKIND = (
    "job_kind added; metrics_observation, origin, delivery and ingest_mode dropped (ADR-0005)"
)
R_API = "api_version added (ADR-0005)"
R_REDACT = "the author identity replaced by author_ref, its payload paths listed in redacted_fields (ADR-0010, Q3)"
R_PARENT = "parent_id and root_id, the parent's and the post's item_id, stamped from the job's post_ref with the key helper; the envelope copies of the post reference go (ADR-0009, ADR-0011)"
R_EDIT = "producers send no edit marker: version, text_hash, content_hash, observation and edit_of go (ADR-0009)"
R_SERIES = "series_step moves into context, a declared key (ADR-0005)"
R_FLAT = "the flat record becomes {envelope, payload}; raw becomes payload (ADR-0005)"


def later(ts: str, seconds: int) -> str:
    t = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ") + timedelta(seconds=seconds)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def envelope(
    service: str,
    kind: str,
    platform: str,
    route: str,
    vendor: str | None,
    fetched_at: str,
    job_id: str,
    retention_class: str,
    raw_ref: str,
    *,
    source_id: str | None = None,
    candidate_key: str | None = None,
    platform_id: str | None = None,
    parent: str | None = None,
    root: str | None = None,
    author_ref: Any = "absent",
    redacted: list[str] | None = None,
    context: dict[str, Any] | None = None,
    client_ids: list[str] | None = None,
    attempt: int = 1,
    job_kind: str = "rotation",
    api_version: str = "v21.0",
    version: str = "1.0.0",
    producer_service: str | None = None,
    produced_at: str | None = None,
    provenance_service: str | None = None,
) -> dict[str, Any]:
    e = meta(S, producer_service or service, job_id, produced_at or later(fetched_at, 2), version)
    e |= {
        "platform": platform,
        "kind": kind,
        "provenance": prov(route, vendor, provenance_service or service, fetched_at),
        "retention_class": retention_class,
        "client_ids": client_ids if client_ids is not None else [CLIENT],
        "job_id": job_id,
        "attempt": attempt,
        "job_kind": job_kind,
        "api_version": api_version,
        "raw_ref": raw_ref,
    }
    if source_id:
        e["source_id"] = source_id
    if candidate_key:
        e["candidate_key"] = candidate_key
    if platform_id is not None:
        e["platform_id"] = platform_id
        if kind in ("post", "video", "comment", "article", "result"):
            e["idempotency_key"] = key(platform, kind, platform_id)
    if parent:
        e["parent_id"] = parent
    if root:
        e["root_id"] = root
    if author_ref != "absent":
        e["author_ref"] = author_ref
    if redacted:
        e["redacted_fields"] = redacted
    if context:
        e["context"] = context
    return e


def msg(env: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    return {"envelope": env, "payload": payload}


FB_PAGE = "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11"
# The public group of fb-keyword-search's PRD example (§5.4 L79), whose platform id stays.
FB_PRD_GROUP = "271936048205533"


def facebook() -> dict[str, Any]:
    p = "docs/prds/facebook/"
    out: dict[str, Any] = {}
    out["fb-page-feed-poller"] = valid(
        S,
        "prd-fb-page-feed-poller",
        msg(
            envelope(
                "fb-page-feed-poller",
                "post",
                "facebook",
                "green",
                None,
                "2026-10-06T09:15:42Z",
                "01J9N2Q7Z4T8X1V6M3K0H5R2WB",
                "meta_on_request",
                rawref("green", "facebook", "2026-10-06", "fb-page-feed-poller", 123, 17),
                source_id=FB_PAGE,
                platform_id="100064583471102_1198837625012734",
            ),
            {
                "id": "100064583471102_1198837625012734",
                "message": "عرض جديد على باقات الإنترنت المنزلي",
                "created_time": "2026-10-06T08:51:40+0000",
            },
        ),
    )
    prd(
        "fb-page-feed-poller",
        p + "fb-page-feed-poller.md",
        110,
        S,
        "prd-fb-page-feed-poller",
        [R_META, R_PROV, R_BATCH, R_JOBKIND, R_API],
    )

    valid(
        S,
        "prd-fb-backfill",
        msg(
            envelope(
                "fb-backfill",
                "post",
                "facebook",
                "green",
                None,
                "2026-10-06T11:02:17Z",
                "01M48DXKW00GHZSJPM5NRWV7R3",
                "meta_on_request",
                "raw/green/facebook/2026/10/06/fb-backfill/000007.jsonl.zst#4",
                source_id=FB_PAGE,
                platform_id="100064583471102_1176002458962861",
                attempt=2,
                job_kind="backfill",
                context={
                    "window": {"start": "2026-07-08T11:00:00Z", "end": "2026-10-06T11:00:00Z"}
                },
            ),
            {
                "id": "100064583471102_1176002458962861",
                "message": "...",
                "created_time": "2026-08-19T14:03:55+0000",
            },
        ),
    )
    prd("fb-backfill", p + "fb-backfill.md", 90, S, "prd-fb-backfill", [R_META, R_PROV, R_API])

    post = "100064583471102_1198837625012734"
    out["fb-client-webhook-receiver"] = valid(
        S,
        "prd-fb-client-webhook-receiver",
        msg(
            envelope(
                "fb-client-webhook-receiver",
                "comment",
                "facebook",
                "green",
                None,
                "2026-10-06T09:23:46Z",
                "01J9N5C4R7V2X8K3M1T6B0QZYF",
                "meta_on_request",
                rawref("green", "facebook", "2026-10-06", "fb-client-webhook-receiver", 208, 3),
                source_id=FB_PAGE,
                platform_id="1198837625012734_5520817364092219",
                parent=iid("facebook", "post", post),
                root=iid("facebook", "post", post),
                author_ref=ref("1000000000000000011", "facebook"),
                redacted=["from"],
                job_kind="push",
            ),
            {
                "item": "comment",
                "verb": "add",
                "post_id": post,
                "comment_id": "1198837625012734_5520817364092219",
                "message": "ممكن تفاصيل الباقة؟",
                "created_time": 1791278623,
            },
        ),
    )
    prd(
        "fb-client-webhook-receiver",
        p + "fb-client-webhook-receiver.md",
        111,
        S,
        "prd-fb-client-webhook-receiver",
        [
            R_META,
            R_PROV,
            R_BATCH,
            "job_kind push for the jobless receiver; delivery and version go (ADR-0005, ADR-0009)",
            R_PARENT,
            "payload_redacted becomes redacted_fields (ADR-0009)",
            R_API,
        ],
    )

    group = "a3d8f0c2-5b17-4e69-8c0d-72e1b94a6f35"
    gpost = "4118203958217764"
    valid(
        S,
        "prd-fb-group-comments-fetcher",
        msg(
            envelope(
                "fb-group-comments-fetcher",
                "comment",
                "facebook",
                "amber",
                "scrapecreators",
                "2026-10-06T10:03:44Z",
                "01J9N4Z6T3K8Q1W5B7D2M9RXHA",
                "vendor_agreed",
                rawref("amber", "facebook", "2026-10-06", "fb-group-comments-fetcher", 31, 12),
                source_id=group,
                platform_id="5520817364092218",
                parent=iid("facebook", "post", gpost),
                root=iid("facebook", "post", gpost),
                author_ref=ref("1000000000000000012", "facebook"),
                redacted=["author"],
                job_kind="comments",
                context={"series_step": "+1h"},
                api_version="scrapecreators-v1",
            ),
            {
                "id": "5520817364092218",
                "text": "…",
                "created_time": "2026-10-06T08:15:02+0000",
                "reply_count": 0,
                "reactions": 3,
            },
        ),
    )
    prd(
        "fb-group-comments-fetcher",
        p + "fb-group-comments-fetcher.md",
        106,
        S,
        "prd-fb-group-comments-fetcher",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_PARENT,
            R_EDIT,
            R_SERIES,
            "payload_redacted becomes redacted_fields (ADR-0009)",
            "job_kind comments (ADR-0005)",
            R_API,
        ],
    )

    valid(
        S,
        "prd-fb-group-posts-poller",
        msg(
            envelope(
                "fb-group-posts-poller",
                "post",
                "facebook",
                "amber",
                "scrapecreators",
                "2026-10-06T09:02:17Z",
                "01J9N4B2M8R5V7Y3D1F6H0KQXE",
                "vendor_agreed",
                rawref("amber", "facebook", "2026-10-06", "fb-group-posts-poller", 52, 8),
                source_id=group,
                platform_id=gpost,
                author_ref=ref("1000000000000000013", "facebook"),
                redacted=["from.id", "from.name"],
                api_version="scrapecreators-v1",
            ),
            {
                "id": gpost,
                "message": "منو عنده تجربة مع انترنت المنصور؟",
                "created_time": "2026-10-06T08:40:11+0000",
            },
        ),
    )
    prd(
        "fb-group-posts-poller",
        p + "fb-group-posts-poller.md",
        104,
        S,
        "prd-fb-group-posts-poller",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_JOBKIND,
            R_API,
            "the poster is an ordinary member here, so its id is replaced by author_ref and listed in redacted_fields; a discovery poster whose clear id stays in the payload carries no author_ref (ADR-0010 L47; Q3)",
        ],
    )

    valid(
        S,
        "prd-fb-keyword-search",
        msg(
            envelope(
                "fb-keyword-search",
                "post",
                "facebook",
                "amber",
                "sociavault",
                "2026-10-06T03:12:48Z",
                "01J9N7E3H2M6T9X1V4K8B0QRWD",
                "vendor_agreed",
                rawref("amber", "facebook", "2026-10-06", "fb-keyword-search", 19, 2),
                source_id="c7e41b95-0a3d-4f82-b6c9-18d5e2a07f43",
                platform_id=gpost,
                context={"query": {"variant": "شركة المثال", "rank": 1}},
                api_version="sociavault-v1",
            ),
            # The PRD's post object (§5.4 L76-L83), a member's post in a public group; the
            # member's id and name are invented (D-8).
            {
                "id": gpost,
                "text": "الإنترنت من شركة المثال بطيء جداً هالأيام، منو عنده نفس المشكلة؟",
                "created_time": "2026-10-06T06:30:12+0000",
                "url": f"https://www.facebook.com/groups/{FB_PRD_GROUP}/posts/{gpost}",
                "author": {"id": "1000000000000000003", "name": "Example Member"},
                "context": {"type": "group", "id": FB_PRD_GROUP, "name": "مجموعة أهالي المنطقة"},
                "reactions": 12,
                "comments": 9,
                "shares": 0,
            },
        ),
    )
    prd(
        "fb-keyword-search",
        p + "fb-keyword-search.md",
        99,
        S,
        "prd-fb-keyword-search",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_JOBKIND,
            R_API,
            "query moves into context, a declared key (ADR-0005)",
            "the poster's id stays in the payload for discovery, so the envelope carries no author_ref; normalize-item computes it (ADR-0010 L47; Q3)",
            "the payload is the post object of §5.4 L76-L83, a member's post with its group context; the member's id and name replaced by invented ones (D-8)",
            "keyword-matcher's container candidate for this post is its group, facebook:group:271936048205533 (discovery.hits/v1/valid/container-group.json; ADR-0031 L34)",
        ],
    )

    # fb-post-comments-fetcher: an id-less comment (ADR-0009); the post id is shortened so the fixture
    # scanner does not read `<digits>:<hash>` as a bot token.
    short_post = "100064583471102_1198837"
    created, text = "2026-10-06T08:41:55+0000", "الله يوفقكم، بس الشبكة ضعيفة بالمنصور من الصبح"
    ck = idless_comment_key("facebook", short_post, created, text)
    pid = ck.split(":", 2)[2]
    valid(
        S,
        "prd-fb-post-comments-fetcher",
        msg(
            envelope(
                "fb-post-comments-fetcher",
                "comment",
                "facebook",
                "green",
                None,
                "2026-10-06T15:20:11Z",
                "01J9N3A8K2P6W4T1X7Z9C0Q5RD",
                "meta_on_request",
                rawref("green", "facebook", "2026-10-06", "fb-post-comments-fetcher", 417, 30),
                source_id=FB_PAGE,
                platform_id=pid,
                parent=iid("facebook", "post", short_post),
                root=iid("facebook", "post", short_post),
                author_ref=None,
                job_kind="comments",
                context={"series_step": "+6h"},
            ),
            {"message": text, "created_time": created, "like_count": 4},
        ),
    )
    prd(
        "fb-post-comments-fetcher",
        p + "fb-post-comments-fetcher.md",
        101,
        S,
        "prd-fb-post-comments-fetcher",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_PARENT,
            R_EDIT,
            R_SERIES,
            R_API,
            "an id-less comment: platform_id is the key's id part, <post id>:<sha256(created_time + text)>, never null (ADR-0009)",
            "the post id is shortened so the fixture scanner does not read <digits>:<hash> as a bot token",
            "author_ref null: the read gives no author id (Q3)",
        ],
    )
    return out


IG_ACCOUNT = "a3d94c10-5e7b-4f28-b6c1-92e0d4a7f835"


def instagram() -> None:
    p = "docs/prds/instagram/"
    valid(
        S,
        "prd-ig-account-media-poller",
        msg(
            envelope(
                "ig-account-media-poller",
                "post",
                "instagram",
                "green",
                None,
                "2026-10-06T09:31:18Z",
                "01J9N3B8K2D5W7Y4T1P6Q0ZRMC",
                "meta_on_request",
                rawref("green", "instagram", "2026-10-06", "ig-account-media-poller", 87, 5),
                source_id=IG_ACCOUNT,
                platform_id="17912345678901234",
            ),
            {
                "id": "17912345678901234",
                "caption": "افتتاح فرعنا الجديد في الكرادة",
                "timestamp": "2026-10-06T08:02:00+0000",
                "like_count": 210,
                "comments_count": 14,
            },
        ),
    )
    prd(
        "ig-account-media-poller",
        p + "ig-account-media-poller.md",
        106,
        S,
        "prd-ig-account-media-poller",
        [R_META, R_PROV, R_BATCH, R_JOBKIND, R_API],
    )

    # ig-comments-fetcher: an id-less vendor comment on a post only the vendor has seen, keyed by its
    # shortcode (ADR-0007, ADR-0009).
    post_pid = "sc:Cx4kQ2LsT9m"
    created, text = "2026-10-06T15:58:12+0000", "اكو عرض للطلاب؟"
    ck = idless_comment_key("instagram", post_pid, created, text)
    valid(
        S,
        "prd-ig-comments-fetcher",
        msg(
            envelope(
                "ig-comments-fetcher",
                "comment",
                "instagram",
                "amber",
                "sociavault",
                "2026-10-06T16:02:31Z",
                "01J9N5D2P8F4Y3A6W9S1V7KJTE",
                "vendor_agreed",
                rawref("amber", "instagram", "2026-10-06", "ig-comments-fetcher", 31, 4),
                source_id="c81f5a27-3d94-4be6-8a02-7e6b1f9d4c33",
                platform_id=ck.split(":", 2)[2],
                parent=iid("instagram", "post", post_pid),
                root=iid("instagram", "post", post_pid),
                author_ref=ref("17841455555555555", "instagram"),
                redacted=["owner"],
                job_kind="comments",
                context={"series_step": "+6h"},
                api_version="sociavault-v1",
            ),
            {"text": text, "created_at": created, "like_count": 2},
        ),
    )
    prd(
        "ig-comments-fetcher",
        p + "ig-comments-fetcher.md",
        95,
        S,
        "prd-ig-comments-fetcher",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_PARENT,
            R_EDIT,
            R_SERIES,
            R_API,
            "an id-less comment keyed <post id>:<sha256(created_time + text)> (ADR-0009); the post is one only the vendor has seen, so its id is sc:<shortcode> (ADR-0007)",
            "the author fields replaced by author_ref (ADR-0010)",
        ],
    )

    valid(
        S,
        "prd-ig-hashtag-search",
        msg(
            envelope(
                "ig-hashtag-search",
                "post",
                "instagram",
                "green",
                None,
                "2026-10-06T09:00:12Z",
                "01J9Q0ZK4V8N3M2X7C5B1A6D9E",
                "meta_on_request",
                rawref("green", "instagram", "2026-10-06", "ig-hashtag-search", 4, 9),
                source_id="6f1c2a4e-9b3d-4c7a-8e21-5a0d3b9f7c11",
                platform_id="17895695668004550",
                client_ids=["2b7e8d1a-4f3c-4a9e-b6d2-1c0e9f8a7b65"],
                context={"edge": "recent_media"},
            ),
            {
                "id": "17895695668004550",
                "caption": "افتتاح الفرع الجديد في المنصور #بغداد #فايبر_اكس",
                "media_type": "IMAGE",
                "media_url": "https://scontent.cdninstagram.com/v/t51/abc.jpg",
                "permalink": "https://www.instagram.com/p/C9xAbCdEfGh/",
                "timestamp": "2026-10-06T08:41:03+0000",
                "like_count": 128,
                "comments_count": 14,
            },
        ),
    )
    prd(
        "ig-hashtag-search",
        p + "ig-hashtag-search.md",
        97,
        S,
        "prd-ig-hashtag-search",
        [
            R_FLAT,
            R_META,
            R_PROV,
            R_JOBKIND,
            R_API,
            "edge moves into context, a declared key (ADR-0005)",
            "raw_ref added (ADR-0005)",
        ],
    )

    valid(
        S,
        "prd-ig-keyword-search",
        msg(
            envelope(
                "ig-keyword-search",
                "post",
                "instagram",
                "amber",
                "sociavault",
                "2026-10-06T03:20:17Z",
                "01J9N9J5T6K8C1E3A5X7Z9QRYM",
                "vendor_agreed",
                rawref("amber", "instagram", "2026-10-06", "ig-keyword-search", 17, 1),
                source_id="d07a3b64-9e12-4c85-b3f0-6a1e8c2d5f97",
                platform_id="3012345678901234567",
                api_version="sociavault-v1",
            ),
            {
                "id": "3012345678901234567",
                "caption": "تجربتي مع شركة المثال",
                "username": "basra.reviews",
            },
        ),
    )
    prd(
        "ig-keyword-search",
        p + "ig-keyword-search.md",
        98,
        S,
        "prd-ig-keyword-search",
        [R_META, R_PROV, R_BATCH, R_JOBKIND, R_API],
    )

    valid(
        S,
        "prd-ig-mentions-fetcher",
        msg(
            envelope(
                "ig-mentions-fetcher",
                "post",
                "instagram",
                "green",
                None,
                "2026-10-06T12:00:41Z",
                "01J9N6E4Q7G9Z1B3X5T8W2MHVF",
                "meta_on_request",
                rawref("green", "instagram", "2026-10-06", "ig-mentions-fetcher", 58, 2),
                source_id="e52b7a90-1c36-4d8f-a7e4-3b9c0d1f6a28",
                platform_id="17895432167098765",
                context={"mention_type": "mentioned_media", "mention_of": "17841405822304914"},
            ),
            {
                "id": "17895432167098765",
                "caption": "شكرا @example_store على الخدمة",
                "timestamp": "2026-10-06T11:40:00+0000",
            },
        ),
    )
    prd(
        "ig-mentions-fetcher",
        p + "ig-mentions-fetcher.md",
        106,
        S,
        "prd-ig-mentions-fetcher",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_JOBKIND,
            R_API,
            "mention_type and mention_of move into context, declared keys (ADR-0005)",
        ],
    )

    media = "17912345678901234"
    valid(
        S,
        "prd-ig-own-comments-fetcher",
        msg(
            envelope(
                "ig-own-comments-fetcher",
                "comment",
                "instagram",
                "green",
                None,
                "2026-10-06T10:31:05Z",
                "01J9N4C6M3E8X2Z5V7R1T9HQAD",
                "meta_on_request",
                rawref("green", "instagram", "2026-10-06", "ig-own-comments-fetcher", 214, 6),
                source_id=IG_ACCOUNT,
                platform_id="17858893269123456",
                parent=iid("instagram", "post", media),
                root=iid("instagram", "post", media),
                author_ref=ref("17841466666666666", "instagram"),
                redacted=["from", "username"],
                job_kind="comments",
                context={"series_step": "+1h"},
            ),
            {
                "id": "17858893269123456",
                "text": "متى يفتح الفرع؟",
                "timestamp": "2026-10-06T10:20:44+0000",
            },
        ),
    )
    prd(
        "ig-own-comments-fetcher",
        p + "ig-own-comments-fetcher.md",
        109,
        S,
        "prd-ig-own-comments-fetcher",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_PARENT,
            R_EDIT,
            R_SERIES,
            R_API,
            "the commenter replaced by author_ref (ADR-0010, Q3)",
        ],
    )

    valid(
        S,
        "prd-ig-webhook-receiver",
        msg(
            envelope(
                "ig-webhook-receiver",
                "comment",
                "instagram",
                "green",
                None,
                "2026-10-06T12:14:08Z",
                "01J9N7F8R2H4A6C9Y1V3X5MKWG",
                "meta_on_request",
                rawref("green", "instagram", "2026-10-06", "ig-webhook-receiver", 412, 1),
                source_id=IG_ACCOUNT,
                platform_id="17858893269123456",
                parent=iid("instagram", "post", media),
                root=iid("instagram", "post", media),
                author_ref=ref("17841466666666666", "instagram"),
                redacted=["from"],
                job_kind="push",
                context={"received_at": "2026-10-06T12:14:07Z"},
            ),
            {
                "field": "comments",
                "value": {
                    "id": "17858893269123456",
                    "text": "متى يفتح الفرع؟",
                    "media": {"id": media},
                },
            },
        ),
    )
    prd(
        "ig-webhook-receiver",
        p + "ig-webhook-receiver.md",
        105,
        S,
        "prd-ig-webhook-receiver",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_PARENT,
            R_EDIT,
            R_API,
            "received_at moves into context, a declared key (ADR-0005)",
            "job_kind push for the jobless receiver; delivery goes (ADR-0005)",
            "the commenter replaced by author_ref (ADR-0010, Q3)",
        ],
    )


LI_CLIENT_PAGE = "3d2f8a14-6b7c-4e19-8a05-c1f7e2b94d36"


def linkedin() -> None:
    p = "docs/prds/linkedin/"
    share = "7247000000000000001"
    valid(
        S,
        "prd-li-client-posts-poller",
        msg(
            envelope(
                "li-client-posts-poller",
                "post",
                "linkedin",
                "green",
                None,
                "2026-10-06T08:20:11Z",
                "01J9N3C5K8W2R7T4Y1B6D0F9GH",
                "linkedin_org",
                rawref("green", "linkedin", "2026-10-06", "li-client-posts-poller", 41, 3),
                source_id=LI_CLIENT_PAGE,
                platform_id=linkedin_post_id(share, "share"),
                api_version="202610",
            ),
            {
                "id": f"urn:li:share:{share}",
                "commentary": "نرحب بعملائنا في فرعنا الجديد",
                "createdAt": 1791264011000,
            },
        ),
    )
    prd(
        "li-client-posts-poller",
        p + "li-client-posts-poller.md",
        107,
        S,
        "prd-li-client-posts-poller",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_JOBKIND,
            R_API,
            "an organisation's post takes linkedin_org on every route (ADR-0055; F-04)",
            "the share-URN key form, selected by the helper's linkedin_urn argument until LI0 decides (ADR-0007; F-28)",
        ],
    )

    activity = "7246999999999999999"
    valid(
        S,
        "prd-li-company-posts-poller",
        msg(
            envelope(
                "li-company-posts-poller",
                "post",
                "linkedin",
                "amber",
                "harvestapi",
                "2026-10-06T08:41:07Z",
                "01J9N3D2M6V4Q8S1X7C5E0A3RJ",
                "linkedin_org",
                rawref("amber", "linkedin", "2026-10-06", "li-company-posts-poller", 7, 11),
                source_id="8a4e1c27-5d3b-4f60-b9a2-7e0c6d1f3a58",
                platform_id=linkedin_post_id(activity, "activity"),
                api_version="harvestapi-v1",
            ),
            {
                "id": activity,
                "text": "Example Bank opens a new branch in Basra",
                "postUrl": f"https://www.linkedin.com/posts/example-bank_activity-{activity}-ab12",
            },
        ),
    )
    prd(
        "li-company-posts-poller",
        p + "li-company-posts-poller.md",
        104,
        S,
        "prd-li-company-posts-poller",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_JOBKIND,
            R_API,
            "the key takes the activity URN, linkedin:post:urn:li:activity:<id> (ADR-0007)",
            "an organisation's post takes linkedin_org, not vendor_agreed (ADR-0055; F-04)",
        ],
    )

    cid = linkedin_comment_id(share, "7247000000000000100", "share")
    valid(
        S,
        "prd-li-notification-receiver",
        msg(
            envelope(
                "li-notification-receiver",
                "comment",
                "linkedin",
                "green",
                None,
                "2026-10-06T15:02:15Z",
                "01J9N5K2W8T4R6Y1B3D7F0GHMQ",
                "linkedin_48h",
                rawref("green", "linkedin", "2026-10-06", "li-notification-receiver", 3, 2),
                source_id=LI_CLIENT_PAGE,
                platform_id=cid,
                parent=iid("linkedin", "post", linkedin_post_id(share, "share")),
                root=iid("linkedin", "post", linkedin_post_id(share, "share")),
                author_ref=ref("urn:li:person:Ab12Cd34", "linkedin"),
                redacted=["actor"],
                job_kind="push",
                api_version="202610",
            ),
            {
                "action": "COMMENT",
                "organizationalEntity": "urn:li:organization:1234567",
                "object": f"urn:li:share:{share}",
                "comment": "متى تفتحون؟",
            },
        ),
    )
    prd(
        "li-notification-receiver",
        p + "li-notification-receiver.md",
        114,
        S,
        "prd-li-notification-receiver",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_PARENT,
            R_API,
            "job_kind push for the jobless receiver (ADR-0005)",
            "the member replaced by author_ref (ADR-0010, Q3)",
        ],
    )

    valid(
        S,
        "prd-li-own-comments-fetcher",
        msg(
            envelope(
                "li-own-comments-fetcher",
                "comment",
                "linkedin",
                "green",
                None,
                "2026-10-06T13:33:02Z",
                "01J9N3F8T2K5W7Y1B4C6D0RGMA",
                "linkedin_48h",
                rawref("green", "linkedin", "2026-10-06", "li-own-comments-fetcher", 19, 7),
                source_id=LI_CLIENT_PAGE,
                platform_id=linkedin_comment_id(share, "7247000000000000099", "share"),
                parent=iid("linkedin", "post", linkedin_post_id(share, "share")),
                root=iid("linkedin", "post", linkedin_post_id(share, "share")),
                author_ref=ref("urn:li:person:Ef56Gh78", "linkedin"),
                redacted=["actor"],
                job_kind="comments",
                context={"series_step": "+6h"},
                api_version="202610",
            ),
            {
                "id": "7247000000000000099",
                "message": {"text": "مبروك الافتتاح"},
                "created": {"time": 1791289982000},
            },
        ),
    )
    prd(
        "li-own-comments-fetcher",
        p + "li-own-comments-fetcher.md",
        107,
        S,
        "prd-li-own-comments-fetcher",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_PARENT,
            R_SERIES,
            R_API,
            "the member replaced by author_ref (ADR-0010, Q3)",
        ],
    )

    valid(
        S,
        "prd-li-post-comments-fetcher",
        msg(
            envelope(
                "li-post-comments-fetcher",
                "comment",
                "linkedin",
                "amber",
                "harvestapi",
                "2026-10-07T08:43:19Z",
                "01J9N4H6P3R8T1V5X7Z0C2DMKE",
                "linkedin_48h",
                rawref("amber", "linkedin", "2026-10-07", "li-post-comments-fetcher", 11, 5),
                source_id="8a4e1c27-5d3b-4f60-b9a2-7e0c6d1f3a58",
                platform_id=linkedin_comment_id(activity, "7246999999999999888", "activity"),
                parent=iid("linkedin", "post", linkedin_post_id(activity, "activity")),
                root=iid("linkedin", "post", linkedin_post_id(activity, "activity")),
                author_ref=ref("ACoAAB1234567", "linkedin"),
                redacted=["author"],
                job_kind="comments",
                context={"series_step": "+24h"},
                api_version="harvestapi-v1",
            ),
            {"id": "7246999999999999888", "text": "Great news for Basra"},
        ),
    )
    prd(
        "li-post-comments-fetcher",
        p + "li-post-comments-fetcher.md",
        109,
        S,
        "prd-li-post-comments-fetcher",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_PARENT,
            R_SERIES,
            R_API,
            "the comment key takes the activity URN form (ADR-0007)",
            "identity: hashed becomes author_ref with redacted_fields (ADR-0009, ADR-0010)",
            "a member's comment takes linkedin_48h on every route (ADR-0055; F-04)",
        ],
    )

    lpost = "7281234567890123456"
    valid(
        S,
        "prd-li-post-search",
        msg(
            envelope(
                "li-post-search",
                "post",
                "linkedin",
                "amber",
                "harvestapi",
                "2026-10-06T03:12:44Z",
                "01M4871WM0G35N2F2R5GBPWABM",
                "linkedin_org",
                rawref("amber", "linkedin", "2026-10-06", "li-post-search", 9, 14),
                source_id="5b2e9c71-4d08-4a3f-9e61-0c7d2b8f4a19",
                platform_id=linkedin_post_id(lpost, "activity"),
                api_version="harvestapi-v1",
            ),
            {
                "url": f"https://www.linkedin.com/posts/example-bank_activity-{lpost}-ab12",
                "text": "post text exactly as returned",
                "postedAt": "2026-10-05T19:40:00Z",
                "author": {
                    "type": "company",
                    "name": "Example Bank",
                    "url": "https://www.linkedin.com/company/example-bank/",
                },
                "engagement": {"reactions": 41, "comments": 6, "reposts": 2},
            },
        ),
    )
    prd(
        "li-post-search",
        p + "li-post-search.md",
        85,
        S,
        "prd-li-post-search",
        [
            R_META,
            R_PROV,
            R_JOBKIND,
            R_API,
            "source_id added: the keyword rule that produced the query (ADR-0004)",
            "platform_id and raw_ref added (ADR-0005)",
            "cost_units goes: the job report carries the cost (ADR-0017)",
            "a company's post takes linkedin_org (ADR-0055; F-04)",
        ],
    )

    # li-org-resolver's sampled post, about a candidate not yet a source (F-03, Q14).
    cand = candidate_key_from_id("linkedin", "urn:li:organization:1234567")
    spost = "7245000000000000123"
    valid(
        S,
        "post-about-a-candidate",
        msg(
            envelope(
                "li-org-resolver",
                "post",
                "linkedin",
                "amber",
                "harvestapi",
                "2026-10-06T10:02:40Z",
                "01M48AMMG0BSDJZYJZ2V3SKTWF",
                "linkedin_org",
                rawref("amber", "linkedin", "2026-10-06", "li-org-resolver", 2, 3),
                candidate_key=cand,
                platform_id=linkedin_post_id(spost, "activity"),
                job_kind="resolve",
                api_version="harvestapi-v1",
            ),
            {"id": spost, "text": "Example Bank results for the third quarter"},
        ),
    )


def news() -> None:
    p = "docs/prds/news/"
    site = "3c7f9d52-1e4a-4b86-a0d3-7b2e5c8f1a90"
    url = "https://www.example-daily.iq/politics/2026/10/06/budget-session?utm_source=rss"
    canonical = "https://www.example-daily.iq/politics/2026/10/06/budget-session"
    akey = article_key(canonical)
    hexid = akey.split(":", 2)[2]
    payload = {
        "url": url,
        "final_url": canonical,
        "canonical_url": canonical,
        "title": "البرلمان يحدد موعد جلسة الموازنة",
        "excerpt": "حدد مجلس النواب يوم الأحد المقبل موعدا لعقد جلسة مخصصة لمناقشة مشروع قانون الموازنة الاتحادية، بحسب بيان لرئاسة المجلس، وسط مطالبات من كتل نيابية بإدراج الخدمات...",
        "excerpt_chars": 247,
        "word_count": 412,
        "author": "فريق التحرير",
        "published_at": "2026-10-06T05:41:00Z",
        "language": "ar",
        "image_urls": ["https://www.example-daily.iq/uploads/2026/10/budget.jpg"],
        "text_full_ref": f"cache/news/2026/10/06/{hexid}.json.zst",
        "text_expires_at": "2026-10-13T05:52:30Z",
        "text_sha256": "5d0c9a7e1b3f4682a1c0d9e7b5f34a86c2d1e0f9a7b5c3d18e6f4a2b0c9d7e53",
        "title_sha256": "b3f60a1d9c7e4825f1a0d3c9b7e65a24d8f1c0b9a7e3d5f21c6b4a0e9d8f7c13",
        "http_status": 200,
        "extractor": "trafilatura",
        "extractor_version": "1.12.2",
    }
    feed_job = "01J9N3A4K8R2T7V5X0M6C1D9HE"
    valid(
        S,
        "prd-news-article-extractor",
        msg(
            envelope(
                "news-article-extractor",
                "article",
                "news",
                "green",
                None,
                "2026-10-06T05:52:30Z",
                feed_job,
                "news_excerpt",
                rawref("green", "news", "2026-10-06", "news-article-extractor", 412, 20),
                source_id=site,
                platform_id=hexid,
                api_version="extract-v1",
                context={
                    "url_key": url_key(url),
                    "access_mode": "direct",
                    "usage_signals": {"search": "yes", "ai_input": "unset", "ai_train": "no"},
                },
            ),
            payload,
        ),
    )
    prd(
        "news-article-extractor",
        p + "news-article-extractor.md",
        91,
        S,
        "prd-news-article-extractor",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_API,
            "a topic-driven producer: job_id is its input message's producer.job_id, attempt its own, job_kind rotation for a URL found live (F-05)",
            "url_key, access_mode and usage_signals move into context, declared keys (ADR-0005, ADR-0068 (c))",
            "url_key recomputed with the one normaliser (Q9)",
            "the article key is news:article:<url_hash of the canonical URL> (ADR-0036)",
        ],
    )

    akey_post = akey
    # news-comments-fetcher: a Disqus comment on the article above.
    valid(
        S,
        "prd-news-comments-fetcher",
        msg(
            envelope(
                "news-comments-fetcher",
                "comment",
                "news",
                "green",
                None,
                "2026-10-06T11:52:40Z",
                "01J9N4B2X7H1M5T8Q3V6D0RYKE",
                "news_excerpt",
                rawref("green", "news", "2026-10-06", "news-comments-fetcher", 64, 9),
                source_id=site,
                platform_id="6203918455",
                parent=iid("news", "article", hexid),
                root=iid("news", "article", hexid),
                author_ref=ref("disqus:9418273650", "news"),
                redacted=["author"],
                job_kind="comments",
                context={"series_step": "+6h"},
                api_version="disqus-3.0",
            ),
            {
                "thread_id": "9418273650",
                "reply_to": None,
                "author_kind": "registered",
                "excerpt": "الخدمة متوقفة في منطقتنا منذ الصباح ولا أحد يرد على الاتصالات",
                "excerpt_chars": 61,
                "text_sha256": "2c8e5f1a9d047b36e0c1f8a5d3b7e94a6f2c0d1b9e5a7f38c4d6b0a2e8f1d975",
                "text_full_ref": f"cache/news/comments/2026/10/06/{hexid}-6h.jsonl.zst",
                "created_at": "2026-10-06T10:31:02Z",
                "likes": 12,
                "dislikes": 1,
            },
        ),
    )
    prd(
        "news-comments-fetcher",
        p + "news-comments-fetcher.md",
        94,
        S,
        "prd-news-comments-fetcher",
        [
            R_META,
            R_PROV,
            R_PARENT,
            R_EDIT,
            R_SERIES,
            R_API,
            "raw_ref added (ADR-0005)",
            "the key drops its :v1 suffix: news:comment:<id> (ADR-0009)",
            "parent_id and root_id are the article's item_id, not its key hex (ADR-0009)",
            "author_hash becomes the envelope's author_ref (ADR-0010; Q3)",
        ],
    )
    _ = akey_post


TT_SOURCE = "3d8a51c2-7e04-4b9f-8c16-2a9e5d70f4b8"


def tiktok() -> None:
    p = "docs/prds/tiktok/"
    vid = "7421538806219533573"
    valid(
        S,
        "prd-tt-client-videos-fetcher",
        msg(
            envelope(
                "tt-client-videos-fetcher",
                "video",
                "tiktok",
                "green",
                None,
                "2026-10-06T09:15:42Z",
                "01J9N7H4S2P9D6K1X8V3B5WEMC",
                "tiktok_display",
                rawref("green", "tiktok", "2026-10-06", "tt-client-videos-fetcher", 31, 8),
                source_id="9a47e0b1-5c3d-4f82-b6e9-1d0c8a3f7e25",
                platform_id=vid,
                api_version="v2",
            ),
            {"id": vid, "title": "عرض الأسبوع", "create_time": 1791278100, "view_count": 1200},
        ),
    )
    prd(
        "tt-client-videos-fetcher",
        p + "tt-client-videos-fetcher.md",
        96,
        S,
        "prd-tt-client-videos-fetcher",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_JOBKIND,
            R_API,
            "kind post becomes video, keyed tiktok:video:<id> (ADR-0007, ADR-0008)",
        ],
    )

    valid(
        S,
        "prd-tt-profile-videos-poller",
        msg(
            envelope(
                "tt-profile-videos-poller",
                "video",
                "tiktok",
                "amber",
                "tikhub",
                "2026-10-06T09:15:42Z",
                "01J9N3A8Q2W6C5Y1T4R7K0D9ZE",
                "vendor_agreed",
                rawref("amber", "tiktok", "2026-10-06", "tt-profile-videos-poller", 45, 2),
                source_id=TT_SOURCE,
                platform_id=vid,
                api_version="tikhub-v1",
            ),
            {"aweme_id": vid, "desc": "عرض الأسبوع", "create_time": 1791278100},
        ),
    )
    prd(
        "tt-profile-videos-poller",
        p + "tt-profile-videos-poller.md",
        107,
        S,
        "prd-tt-profile-videos-poller",
        [R_META, R_PROV, R_BATCH, R_JOBKIND, R_API, "kind post becomes video (ADR-0007, ADR-0008)"],
    )

    valid(
        S,
        "prd-tt-hashtag-feed-poller",
        msg(
            envelope(
                "tt-hashtag-feed-poller",
                "video",
                "tiktok",
                "amber",
                "ensembledata",
                "2026-10-06T09:00:41Z",
                "01M4872SXGZPDRA21SXW1ZYD7N",
                "vendor_agreed",
                rawref("amber", "tiktok", "2026-10-06", "tt-hashtag-feed-poller", 12, 40),
                source_id="9b1e4d2c-7a3f-4e8b-b2c1-5f6a7d8e9c01",
                platform_id="7420000000000000456",
                context={
                    "hashtag_id": "1650000000000000002",
                    "hashtag_name": "زين_الخير",
                    "page": 1,
                },
                api_version="ensembledata-v1",
            ),
            {
                "aweme_id": "7420000000000000456",
                "desc": "#زين_الخير حملة التبرعات بالموصل",
                "create_time": 1759735200,
                "author": {
                    "uid": "6800000000000000777",
                    "unique_id": "mosul.daily",
                    "follower_count": 120500,
                    "verification_type": 1,
                },
                "statistics": {
                    "play_count": 40100,
                    "digg_count": 2210,
                    "comment_count": 310,
                    "share_count": 95,
                },
                "text_extra": [{"hashtag_name": "زين_الخير", "hashtag_id": "1650000000000000002"}],
            },
        ),
    )
    prd(
        "tt-hashtag-feed-poller",
        p + "tt-hashtag-feed-poller.md",
        81,
        S,
        "prd-tt-hashtag-feed-poller",
        [
            R_FLAT,
            R_META,
            R_PROV,
            R_API,
            "raw_ref and job_kind added (ADR-0005)",
            "source_type goes: the source row holds it (ADR-0005)",
            "context backfill goes: job_kind says it (ADR-0005)",
            "the poster's id stays in the payload for discovery, so no author_ref (ADR-0010 L47)",
            "client_ids added (ADR-0005)",
        ],
    )

    valid(
        S,
        "prd-tt-keyword-search",
        msg(
            envelope(
                "tt-keyword-search",
                "video",
                "tiktok",
                "amber",
                "tikhub",
                "2026-10-06T14:05:12Z",
                "01M48RGBQ08KKPCN8S96112V4X",
                "vendor_agreed",
                rawref("amber", "tiktok", "2026-10-06", "tt-keyword-search", 77, 3),
                source_id="3f9c2a1e-6b4d-4f7a-9c1e-2d5b8a7e4c10",
                platform_id="7421000000000000123",
                context={"variant": "زين عراق", "country": "IQ", "page": 2},
                api_version="tikhub-v1",
            ),
            {
                "aweme_id": "7421000000000000123",
                "desc": "تجربتي مع انترنت زين بالبصرة...",
                "create_time": 1759750800,
                "author": {
                    "uid": "6800000000000000001",
                    "unique_id": "basra.reviews",
                    "follower_count": 48200,
                    "verification_type": 0,
                },
                "statistics": {
                    "play_count": 15300,
                    "digg_count": 912,
                    "comment_count": 87,
                    "share_count": 41,
                },
                "region": "IQ",
            },
        ),
    )
    prd(
        "tt-keyword-search",
        p + "tt-keyword-search.md",
        75,
        S,
        "prd-tt-keyword-search",
        [
            R_FLAT,
            R_META,
            R_PROV,
            R_API,
            "raw_ref and job_kind added (ADR-0005)",
            "source_type goes (ADR-0005)",
            "context keyword_id goes: the rule's source_id names it (ADR-0044; F-35)",
            "client_ids added (ADR-0005)",
        ],
    )

    cid = "7421601187764085510"
    valid(
        S,
        "prd-tt-video-comments-fetcher",
        msg(
            envelope(
                "tt-video-comments-fetcher",
                "comment",
                "tiktok",
                "amber",
                "tikhub",
                "2026-10-06T15:20:08Z",
                "01J9N4C2M7X0B8E5V1Q3S6TKHD",
                "vendor_agreed",
                rawref("amber", "tiktok", "2026-10-06", "tt-video-comments-fetcher", 212, 6),
                source_id=TT_SOURCE,
                platform_id=cid,
                parent=iid("tiktok", "video", vid),
                root=iid("tiktok", "video", vid),
                author_ref=ref("6800000000000000999", "tiktok"),
                redacted=["user"],
                job_kind="comments",
                context={"series_step": "+6h"},
                api_version="tikhub-v1",
            ),
            {"cid": cid, "text": "وين الفرع؟", "create_time": 1791300000},
        ),
    )
    prd(
        "tt-video-comments-fetcher",
        p + "tt-video-comments-fetcher.md",
        99,
        S,
        "prd-tt-video-comments-fetcher",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_PARENT,
            R_EDIT,
            R_SERIES,
            R_API,
            "the commenter replaced by author_ref (ADR-0010, Q3)",
        ],
    )


def telegram() -> None:
    p = "docs/prds/telegram/"
    owned = "8c41f2d7-5a3e-4b96-a0d1-7e2c9b3f4a58"
    post = telegram_post_id("iq_example_owned", "5127")
    valid(
        S,
        "prd-tg-bot-channel-receiver",
        msg(
            envelope(
                "tg-bot-channel-receiver",
                "post",
                "telegram",
                "green",
                None,
                "2026-10-06T09:15:02Z",
                "01M487XDFG8JDZ667B758J62C2",
                "telegram_bot",
                rawref("green", "telegram", "2026-10-06", "tg-bot-channel-receiver", 311, 4),
                source_id=owned,
                platform_id=post,
                job_kind="push",
                api_version="bot-api-9",
                context={"update_id": 704118532},
            ),
            {
                "message_id": 5127,
                "chat": {"id": -1001849302001, "username": "iq_example_owned", "type": "channel"},
                "date": 1791278100,
                "text": "عرض جديد",
            },
        ),
    )
    prd(
        "tg-bot-channel-receiver",
        p + "tg-bot-channel-receiver.md",
        115,
        S,
        "prd-tg-bot-channel-receiver",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_API,
            "job_kind push for the jobless receiver; event and ingest_mode go (ADR-0005, ADR-0009)",
            "telegram_bot replaces vendor_agreed on the bot's records (ADR-0054)",
            "owned_by_client goes: the source row holds it (ADR-0005, ADR-0013)",
        ],
    )

    group_msg = telegram_comment_id("-1001849302999", "9312")
    valid(
        S,
        "prd-tg-discussion-receiver",
        msg(
            envelope(
                "tg-discussion-receiver",
                "comment",
                "telegram",
                "green",
                None,
                "2026-10-06T09:20:11Z",
                "01M4886V7RNKF111FA2SGP78XR",
                "telegram_bot",
                rawref("green", "telegram", "2026-10-06", "tg-discussion-receiver", 87, 2),
                source_id=owned,
                platform_id=group_msg,
                parent=iid("telegram", "post", post),
                root=iid("telegram", "post", post),
                author_ref=ref("5210987654", "telegram"),
                redacted=["from"],
                job_kind="push",
                api_version="bot-api-9",
                context={
                    "update_id": 704118977,
                    "discussion_source_id": "d2e96b1a-47c0-4f8d-b35a-0c71e8a49f26",
                },
            ),
            {
                "message_id": 9312,
                "chat": {"id": -1001849302999, "type": "supergroup"},
                "date": 1791278411,
                "text": "متى يبدأ العرض؟",
                "reply_to_message": {"message_id": 9301},
            },
        ),
    )
    prd(
        "tg-discussion-receiver",
        p + "tg-discussion-receiver.md",
        116,
        S,
        "prd-tg-discussion-receiver",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_PARENT,
            R_API,
            "job_kind push; event and ingest_mode go (ADR-0005)",
            "discussion_source_id moves into context; unthreaded goes: a comment always has a parent, so a parentless one is parked, not published (F-33)",
            "minimized becomes author_ref with redacted_fields (ADR-0009, ADR-0010)",
            "telegram_bot replaces vendor_agreed (ADR-0054)",
        ],
    )

    valid(
        S,
        "prd-tg-channel-posts-poller",
        msg(
            envelope(
                "tg-channel-posts-poller",
                "post",
                "telegram",
                "amber",
                "tugelbay",
                "2026-10-06T09:21:17Z",
                "01J9N5C3R8V2K7T4X0M6Q1HZDE",
                "vendor_agreed",
                rawref("amber", "telegram", "2026-10-06", "tg-channel-posts-poller", 45, 13),
                source_id="3a7d9e54-6c0b-4f12-8e37-b1c24d90f6a8",
                platform_id=telegram_post_id("iq_example_news", "48213"),
                api_version="tugelbay-actor-2",
            ),
            {
                "id": 48213,
                "channel": "iq_example_news",
                "text": "انقطاع الكهرباء في البصرة",
                "views": 8410,
            },
        ),
    )
    prd(
        "tg-channel-posts-poller",
        p + "tg-channel-posts-poller.md",
        109,
        S,
        "prd-tg-channel-posts-poller",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_JOBKIND,
            R_API,
            "the vendor spelt apify_tugelbay becomes tugelbay (ADR-0051 (c))",
        ],
    )


X_SOURCE = "a4d2c9e1-5b7f-4e3a-8c60-2f1b9d7e4a35"


def x() -> None:
    p = "docs/prds/x/"
    valid(
        S,
        "prd-x-user-timeline-poller",
        msg(
            envelope(
                "x-user-timeline-poller",
                "post",
                "x",
                "green",
                None,
                "2026-10-06T07:00:41Z",
                "01J9P4K8W2R6T0Y3N7B5D1F9HC",
                "x_24h_sync",
                rawref("green", "x", "2026-10-06", "x-user-timeline-poller", 87, 21),
                source_id=X_SOURCE,
                platform_id="2107360526334088839",
                api_version="2",
                context={"paid": True},
            ),
            {
                "id": "2107360526334088839",
                "text": "تخفيضات نهاية الأسبوع في جميع الفروع",
                "author_id": "1456789012345678901",
                "created_at": "2026-10-06T06:58:02.000Z",
            },
        ),
    )
    prd(
        "x-user-timeline-poller",
        p + "x-user-timeline-poller.md",
        114,
        S,
        "prd-x-user-timeline-poller",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_JOBKIND,
            R_API,
            "paid moves into context, a declared key (ADR-0005)",
        ],
    )

    valid(
        S,
        "prd-x-filtered-stream",
        msg(
            envelope(
                "x-filtered-stream",
                "post",
                "x",
                "green",
                None,
                "2026-10-06T10:12:04Z",
                "01M48B5V90W8B91YHW3K3BNVR2",
                "x_24h_sync",
                rawref("green", "x", "2026-10-06", "x-filtered-stream", 412, 7),
                source_id=X_SOURCE,
                platform_id="2107413571090333696",
                job_kind="stream",
                api_version="2",
                context={
                    "connection_id": "01J9PB7XQ3M8D2V6K0R4T1H5ZW",
                    "paid": True,
                    "matching_rules": [
                        {
                            "id": "1843102937465028608",
                            "tag": "v1|acct|p1|s=a4d2c9e1-5b7f-4e3a-8c60-2f1b9d7e4a35,0b6e2d71-93c4-4f8a-b215-7d40e9c3a6f2|c=3e8f1a2b-7c4d-4b9e-a1f0-6d2c5e8b7a14,9d27c4e0-1f6a-4b83-8e5d-c0a2b7f41936",
                        },
                        {
                            "id": "1843103311892615168",
                            "tag": "v1|brand|p1|s=6c19f0a4-2e8b-4d57-9a3c-b1e7d52f8064|c=3e8f1a2b-7c4d-4b9e-a1f0-6d2c5e8b7a14",
                        },
                    ],
                },
                client_ids=["3e8f1a2b-7c4d-4b9e-a1f0-6d2c5e8b7a14"],
            ),
            {
                "data": {"id": "2107413571090333696", "text": "وصل العرض الجديد لفرع البصرة"},
                "matching_rules": [{"id": "1843102937465028608"}],
            },
        ),
    )
    prd(
        "x-filtered-stream",
        p + "x-filtered-stream.md",
        113,
        S,
        "prd-x-filtered-stream",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_API,
            "job_kind stream for the stream (ADR-0005)",
            "matching_rules and paid move into context beside connection_id (ADR-0005)",
        ],
    )

    valid(
        S,
        "prd-x-full-archive-search",
        msg(
            envelope(
                "x-full-archive-search",
                "post",
                "x",
                "green",
                None,
                "2026-10-06T09:14:22Z",
                "01J9P7Q3M5X8C2V6B9N4K1H0TZ",
                "x_24h_sync",
                rawref("green", "x", "2026-10-06", "x-full-archive-search", 12, 30),
                source_id="c71e5a90-3d2b-4f86-9a14-8e0b6d2f5c37",
                platform_id="2087514290017763328",
                job_kind="backfill",
                api_version="2",
                context={"paid": True},
                client_ids=["3e8f1a2b-7c4d-4b9e-a1f0-6d2c5e8b7a14"],
            ),
            {
                "id": "2087514290017763328",
                "text": "افتتاح فرعنا الجديد",
                "created_at": "2026-08-12T10:00:00.000Z",
            },
        ),
    )
    prd(
        "x-full-archive-search",
        p + "x-full-archive-search.md",
        108,
        S,
        "prd-x-full-archive-search",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_API,
            "metrics_observation goes; job_kind stays backfill (ADR-0005)",
            "paid moves into context (ADR-0005)",
        ],
    )

    valid(
        S,
        "prd-x-recent-search",
        msg(
            envelope(
                "x-recent-search",
                "post",
                "x",
                "green",
                None,
                "2026-10-06T09:15:04Z",
                "01M487XBH07GQE33JRM29CMCMZ",
                "x_24h_sync",
                rawref("green", "x", "2026-10-06", "x-recent-search", 42, 310),
                source_id="7c1d9a2e-55b4-4f1e-8a0c-3e9f6b2d4a71",
                platform_id="1843201122334455667",
                api_version="2",
                context={"query_arm": "ar", "matched_terms": ["دجلة تيليكوم"], "paid": True},
            ),
            {
                "id": "1843201122334455667",
                "text": "شبكة دجلة تيليكوم بالبصرة صارت أحسن من قبل بس السعر غالي",
                "author_id": "1000000000000000001",
                "conversation_id": "1843201122334455667",
                "created_at": "2026-10-06T09:02:31.000Z",
                "lang": "ar",
                "public_metrics": {
                    "retweet_count": 2,
                    "reply_count": 5,
                    "like_count": 38,
                    "quote_count": 1,
                },
                "includes": {
                    "users": [{"id": "1000000000000000001", "username": "example_poster_x"}]
                },
            },
        ),
    )
    prd(
        "x-recent-search",
        p + "x-recent-search.md",
        100,
        S,
        "prd-x-recent-search",
        [
            R_FLAT,
            R_META,
            R_PROV,
            R_API,
            "raw_ref and job_kind added (ADR-0005)",
            "source_type, budget_tag and cost_units go (ADR-0005, ADR-0017)",
            "discovery_hit_emitted goes (ADR-0031); paid moves into context",
            "includes move inside the payload (ADR-0005)",
            "the poster's id stays in the payload for discovery, so no author_ref (ADR-0010 L47)",
            "the poster's handle and id replaced by invented ones (D-8)",
        ],
    )

    post, reply = "1975163027415552001", "1975210483926617088"
    valid(
        S,
        "prd-x-replies-fetcher",
        msg(
            envelope(
                "x-replies-fetcher",
                "comment",
                "x",
                "green",
                None,
                "2026-10-06T18:31:07Z",
                "01J9Q2M7T4X8B1R6V0Z3N5K9WD",
                "x_24h_sync",
                rawref("green", "x", "2026-10-06", "x-replies-fetcher", 112, 18),
                source_id="7c2e9a41-3b6d-4f8e-a1c5-0d9b2e6f4a73",
                platform_id=reply,
                parent=iid("x", "post", post),
                root=iid("x", "post", post),
                author_ref=ref("1290000000000000077", "x"),
                redacted=[
                    "author_id",
                    "in_reply_to_user_id",
                    "entities.mentions.id",
                    "entities.mentions.username",
                    "includes.users",
                ],
                job_kind="comments",
                context={"series_step": "+6h", "paid": True},
                api_version="2",
                client_ids=["5e1a7c3d-9b2f-4d6e-8a0c-3f7b1e9d2a64"],
            ),
            {
                "id": reply,
                "text": "نفس المشكلة عندي",
                "conversation_id": post,
                "created_at": "2026-10-06T18:10:00.000Z",
            },
        ),
    )
    prd(
        "x-replies-fetcher",
        p + "x-replies-fetcher.md",
        108,
        S,
        "prd-x-replies-fetcher",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_PARENT,
            R_EDIT,
            R_SERIES,
            R_API,
            "the key is x:post:<id> for every tweet, a reply's item kind comment (ADR-0007, ADR-0008)",
            "ledger_key, author_source_id, author_is_source and in_reply_to_ref go (ADR-0064, ADR-0010)",
            "conversation_id stays in the payload (F-36)",
            "removed_fields becomes redacted_fields; author_ref takes the helper's 64-hex form (ADR-0009, ADR-0010)",
            "paid moves into context",
        ],
    )


YT_SOURCE = "3a9e5c1d-7f2b-4e8a-b6d0-91c4f2e7a835"


def youtube() -> None:
    p = "docs/prds/youtube/"
    valid(
        S,
        "prd-yt-keyword-search",
        msg(
            envelope(
                "yt-keyword-search",
                "video",
                "youtube",
                "green",
                None,
                "2026-10-06T03:04:11Z",
                "01M47JP18081JQQZ19WYHA1ZH3",
                "youtube_30d_text",
                rawref("green", "youtube", "2026-10-06", "yt-keyword-search", 3, 12),
                source_id="3f1c2a6e-9d2b-4c1e-9a6f-2b7d8e5f4a10",
                platform_id="dQw4w9WgXcQ",
                api_version="v3",
                context={"partial": True},
            ),
            {
                "kind": "youtube#searchResult",
                "id": {"videoId": "dQw4w9WgXcQ"},
                "snippet": {
                    "publishedAt": "2026-10-06T01:12:00Z",
                    "channelId": "UCuAXFkgsw1L7xaCfnd5JJOw",
                    "title": "...",
                    "description": "...",
                },
            },
        ),
    )
    prd(
        "yt-keyword-search",
        p + "yt-keyword-search.md",
        100,
        S,
        "prd-yt-keyword-search",
        [
            R_FLAT,
            R_META,
            R_PROV,
            R_API,
            "raw_ref and job_kind added (ADR-0005)",
            "partial moves into context (ADR-0065 b))",
            "origin, source_type and cost_units go (ADR-0005, ADR-0017)",
            "channel_id stays in the payload (F-36)",
            "client_ids added",
        ],
    )

    valid(
        S,
        "prd-yt-pubsub-receiver",
        msg(
            envelope(
                "yt-pubsub-receiver",
                "video",
                "youtube",
                "green",
                None,
                "2026-10-06T09:12:44Z",
                "01J9N7QV8D2K6M4P0R3S5T7W9X",
                "youtube_30d_text",
                rawref("green", "youtube", "2026-10-06", "yt-pubsub-receiver", 117, 3),
                source_id="3c9a7e52-1f4b-4d8e-b6a0-8e2f5c1d7a94",
                platform_id="k7Qm2Xv9TbE",
                job_kind="push",
                api_version="pubsubhubbub-0.4",
                context={"partial": True},
                client_ids=["9e4d2b17-6a3c-4f81-a5d9-2c7b0e6f3a18"],
            ),
            {
                "id": "yt:video:k7Qm2Xv9TbE",
                "yt:videoId": "k7Qm2Xv9TbE",
                "yt:channelId": "UCx3Kp9vQ2mLwR7tYb4nJ8sA",
                "title": "جولة في سوق الشورجة قبل العيد",
                "link": "https://www.youtube.com/watch?v=k7Qm2Xv9TbE",
                "published": "2026-10-06T09:12:03+00:00",
                "updated": "2026-10-06T09:12:41.118204512+00:00",
            },
        ),
    )
    prd(
        "yt-pubsub-receiver",
        p + "yt-pubsub-receiver.md",
        104,
        S,
        "prd-yt-pubsub-receiver",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_API,
            "kind post becomes video, keyed youtube:video:<id> (ADR-0007, ADR-0008)",
            "job_kind push; delivery and version go (ADR-0005, ADR-0009)",
            "partial moves into context (ADR-0065 b))",
            "parent_platform_id goes (ADR-0009)",
        ],
    )

    valid(
        S,
        "prd-yt-uploads-reconciler",
        msg(
            envelope(
                "yt-uploads-reconciler",
                "video",
                "youtube",
                "green",
                None,
                "2026-10-06T11:04:27Z",
                "01J9P4D2R7X5K8M1Q3V6T0B9ZC",
                "youtube_30d_text",
                rawref("green", "youtube", "2026-10-06", "yt-uploads-reconciler", 45, 6),
                source_id="a3d9f1c4-5e27-4b8a-9f60-2c1e7d4b8a93",
                platform_id="Xk3vQ9pL2aE",
                job_kind="reconciliation",
                api_version="v3",
                context={"partial": True},
            ),
            {
                "kind": "youtube#playlistItem",
                "snippet": {
                    "resourceId": {"videoId": "Xk3vQ9pL2aE"},
                    "publishedAt": "2026-10-06T10:58:00Z",
                },
            },
        ),
    )
    prd(
        "yt-uploads-reconciler",
        p + "yt-uploads-reconciler.md",
        110,
        S,
        "prd-yt-uploads-reconciler",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_API,
            "kind post becomes video (ADR-0007, ADR-0008)",
            "partial moves into context; metrics_observation goes (ADR-0005, ADR-0065)",
        ],
    )

    valid(
        S,
        "prd-yt-video-details-fetcher",
        msg(
            envelope(
                "yt-video-details-fetcher",
                "video",
                "youtube",
                "green",
                None,
                "2026-10-06T07:14:03Z",
                "01JAB3K7T2W9M4Q8R1X5Y6Z0NC",
                "youtube_30d_text",
                rawref("green", "youtube", "2026-10-06", "yt-video-details-fetcher", 210, 4),
                source_id="2b7d4e90-1c3a-4f6e-8d25-7a9b0c1e3f42",
                platform_id="Xy12AbCdEfG",
                job_kind="first_sight",
                api_version="v3",
                context={
                    "live_state": "none",
                    "call_id": "01JAB3K7V0H5D2E8F1G3J4K6MN",
                    "completes_partial_from": "yt-pubsub-receiver",
                },
            ),
            {
                "id": "Xy12AbCdEfG",
                "snippet": {
                    "publishedAt": "2026-10-06T07:12:09Z",
                    "channelId": "UCq3Ov8nVbT0xY1zKp2LmA4w",
                    "title": "جولة في سوق الشورجة",
                    "description": "جولة مصورة في أقدم أسواق بغداد",
                    "tags": ["بغداد", "الشورجة"],
                    "defaultAudioLanguage": "ar",
                    "liveBroadcastContent": "none",
                    "thumbnails": {
                        "high": {"url": "https://i.ytimg.com/vi/Xy12AbCdEfG/hqdefault.jpg"}
                    },
                },
                "contentDetails": {"duration": "PT12M41S"},
                "statistics": {"viewCount": "312", "likeCount": "41", "commentCount": "6"},
                "topicDetails": {"topicCategories": ["https://en.wikipedia.org/wiki/Society"]},
            },
        ),
    )
    prd(
        "yt-video-details-fetcher",
        p + "yt-video-details-fetcher.md",
        92,
        S,
        "prd-yt-video-details-fetcher",
        [
            R_META,
            R_PROV,
            R_API,
            "kind post becomes video (ADR-0007, ADR-0008)",
            "raw_ref added (ADR-0005)",
            "live_state, call_id and completes_partial_from move into context; partial: false and metrics_observation go (ADR-0005, ADR-0065)",
            "client_ids added",
        ],
    )

    video = "q3Vt8LmZ2xA"
    top = "UgzK7pQ2mV9xR4tL1bN6AaABAg"
    valid(
        S,
        "prd-yt-comments-fetcher",
        msg(
            envelope(
                "yt-comments-fetcher",
                "comment",
                "youtube",
                "green",
                None,
                "2026-10-07T07:03:11Z",
                "01J9P4D2K8W6Y3N0Q5T7V1X9ZC",
                "youtube_30d_text",
                rawref("green", "youtube", "2026-10-07", "yt-comments-fetcher", 57, 1),
                source_id=YT_SOURCE,
                platform_id=top,
                parent=iid("youtube", "video", video),
                root=iid("youtube", "video", video),
                author_ref=ref("UCaaaaaaaaaaaaaaaaaaaaaa", "youtube"),
                redacted=[
                    "snippet.topLevelComment.snippet.authorChannelId",
                    "snippet.topLevelComment.snippet.authorDisplayName",
                    "snippet.topLevelComment.snippet.authorProfileImageUrl",
                    "snippet.topLevelComment.snippet.authorChannelUrl",
                ],
                job_kind="comments",
                api_version="v3",
                context={"series_step": "+24h", "video_channel_id": "UC7xQe2lW9pK3bN5aV1rT8sQ"},
            ),
            {
                "id": top,
                "snippet": {
                    "videoId": video,
                    "topLevelComment": {
                        "id": top,
                        "snippet": {
                            "textOriginal": "حلو الفيديو",
                            "publishedAt": "2026-10-07T06:40:00Z",
                        },
                    },
                    "totalReplyCount": 1,
                },
            },
        ),
    )
    prd(
        "yt-comments-fetcher",
        p + "yt-comments-fetcher.md",
        112,
        S,
        "prd-yt-comments-fetcher",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_PARENT,
            R_EDIT,
            R_SERIES,
            R_API,
            "video_channel_id moves into context (F-25)",
            "removed_fields becomes redacted_fields with the full payload paths (ADR-0009)",
            "author_is_source goes (ADR-0010)",
            "author_ref takes the helper's 64-hex form",
        ],
    )

    valid(
        S,
        "prd-yt-replies-fetcher",
        msg(
            envelope(
                "yt-replies-fetcher",
                "comment",
                "youtube",
                "green",
                None,
                "2026-10-07T07:05:42Z",
                "01J9P4F7M2R8T5W0Y3B6D9H1KN",
                "youtube_30d_text",
                rawref("green", "youtube", "2026-10-07", "yt-replies-fetcher", 31, 2),
                source_id=YT_SOURCE,
                platform_id=f"{top}.9TqNw5Hc3Kp",
                parent=iid("youtube", "comment", top),
                root=iid("youtube", "video", video),
                author_ref=ref("UCbbbbbbbbbbbbbbbbbbbbbb", "youtube"),
                redacted=[
                    "snippet.authorChannelId",
                    "snippet.authorDisplayName",
                    "snippet.authorProfileImageUrl",
                    "snippet.authorChannelUrl",
                ],
                job_kind="replies",
                api_version="v3",
                context={"series_step": "+24h", "video_channel_id": "UC7xQe2lW9pK3bN5aV1rT8sQ"},
            ),
            {
                "id": f"{top}.9TqNw5Hc3Kp",
                "snippet": {
                    "textOriginal": "صحيح",
                    "parentId": top,
                    "publishedAt": "2026-10-07T06:55:00Z",
                },
            },
        ),
    )
    prd(
        "yt-replies-fetcher",
        p + "yt-replies-fetcher.md",
        101,
        S,
        "prd-yt-replies-fetcher",
        [
            R_META,
            R_PROV,
            R_BATCH,
            R_PARENT,
            R_EDIT,
            R_SERIES,
            R_API,
            "a reply's parent_id is its parent comment's item_id, root_id the video's (ADR-0009)",
            "video_channel_id moves into context (F-25)",
        ],
    )


def resolvers_and_web() -> None:
    # A resolver's archived lookup (ADR-0032): a profile record about a candidate.
    cand = candidate_key_from_handle("instagram", "furat_restaurant")
    valid(
        S,
        "profile",
        msg(
            envelope(
                "ig-account-resolver",
                "profile",
                "instagram",
                "green",
                None,
                "2026-10-06T12:40:11Z",
                "01J9N8H3S5J7B9D2Z4W6Y8NPXK",
                "meta_on_request",
                rawref("green", "instagram", "2026-10-06", "ig-account-resolver", 9, 1),
                candidate_key=cand,
                job_kind="resolve",
            ),
            {
                "business_discovery": {
                    "id": "17841400112233445",
                    "username": "furat_restaurant",
                    "followers_count": 48200,
                    "media_count": 913,
                }
            },
        ),
    )
    # A web engine's response, keyed by the rule's source_id and the request time (ADR-0005, ADR-0037).
    valid(
        S,
        "search-response",
        msg(
            envelope(
                "web-search-mojeek",
                "search_response",
                "web",
                "green",
                "mojeek",
                "2026-10-06T04:02:50Z",
                "01M47P07P0M1V49VADF6SRK5BM",
                "news_excerpt",
                rawref("green", "web", "2026-10-06", "web-search-mojeek", 7, 41),
                source_id="7d2b0c4e-1f3a-4b5c-8d6e-9f0a1b2c3d4e",
                api_version="mojeek-v1",
            ),
            {
                "response": {
                    "head": {"query": '"فايبر اكس" العراق', "results": 10},
                    "results": [{"title": "فايبر اكس تطلق باقة جديدة في واسط"}],
                }
            },
        ),
    )
    # web-commoncrawl-scanner's per-host aggregate: no rule, keyed by the site's candidate key (F-31).
    valid(
        S,
        "search-response-commoncrawl",
        msg(
            envelope(
                "web-commoncrawl-scanner",
                "search_response",
                "web",
                "green",
                None,
                "2026-10-09T02:14:50Z",
                "01M4F71ZR0Q8N3K5D2B7T4W9XC",
                "news_excerpt",
                rawref("green", "web", "2026-10-09", "web-commoncrawl-scanner", 2, 6),
                candidate_key=news_site_candidate_key("example-daily.iq"),
                client_ids=[],
                api_version="cc-index-1",
                context={"crawl_id": "CC-MAIN-2026-38", "host": "www.example-daily.iq"},
            ),
            {"captures": 1840, "first_capture": "2026-09-14", "last_capture": "2026-09-27"},
        ),
    )
    # li-notification-receiver's reaction event, archive-only (ADR-0008).
    valid(
        S,
        "reaction",
        msg(
            envelope(
                "li-notification-receiver",
                "reaction",
                "linkedin",
                "green",
                None,
                "2026-10-06T15:04:00Z",
                "01J9N5K9W8T4R6Y1B3D7F0GHMR",
                "linkedin_48h",
                rawref("green", "linkedin", "2026-10-06", "li-notification-receiver", 3, 5),
                source_id=LI_CLIENT_PAGE,
                platform_id="urn:li:activityEvent:7247000000000000777",
                author_ref=ref("urn:li:person:Ij90Kl12", "linkedin"),
                redacted=["actor"],
                job_kind="push",
                api_version="202610",
            ),
            {"action": "LIKE", "object": "urn:li:share:7247000000000000001"},
        ),
    )
    # A count-only read archived as `metrics` (ADR-0034), naming the observed item's key.
    valid(
        S,
        "metrics",
        msg(
            envelope(
                "fb-reactions-fetcher",
                "metrics",
                "facebook",
                "green",
                None,
                "2026-10-07T07:14:51Z",
                "01J9Q1M4V8N2B6X0C3Z7A5S9DF",
                "meta_on_request",
                rawref("green", "facebook", "2026-10-07", "fb-reactions-fetcher", 15, 3),
                source_id=FB_PAGE,
                job_kind="metrics",
                context={"item_key": key("facebook", "post", "100064583471102_1198837625012734")},
            ),
            {
                "id": "100064583471102_1198837625012734",
                "reactions": {"summary": {"total_count": 2421}},
            },
        ),
    )
    # A backfilled first sight carries job_kind backfill (ADR-0065 L37; F-06).
    valid(
        S,
        "video-first-sight-backfill",
        msg(
            envelope(
                "yt-video-details-fetcher",
                "video",
                "youtube",
                "green",
                None,
                "2026-10-06T07:30:03Z",
                "01JAB3M2T2W9M4Q8R1X5Y6Z0ND",
                "youtube_30d_text",
                rawref("green", "youtube", "2026-10-06", "yt-video-details-fetcher", 211, 1),
                source_id="a3d9f1c4-5e27-4b8a-9f60-2c1e7d4b8a93",
                platform_id="Pq83LmZ2xAb",
                job_kind="backfill",
                api_version="v3",
            ),
            {"id": "Pq83LmZ2xAb", "snippet": {"publishedAt": "2026-08-01T10:00:00Z"}},
        ),
    )
    # A client's revoked TikTok account read by the vendor in fallback takes the vendor route's class
    # (ADR-0035 L33; F-04).
    valid(
        S,
        "video-fallback-vendor-agreed",
        msg(
            envelope(
                "tt-profile-videos-poller",
                "video",
                "tiktok",
                "amber",
                "tikhub",
                "2026-10-06T12:00:00Z",
                "01J9N3A8Q2W6C5Y1T4R7K0DA0E",
                "vendor_agreed",
                rawref("amber", "tiktok", "2026-10-06", "tt-profile-videos-poller", 46, 1),
                source_id="9a47e0b1-5c3d-4f82-b6e9-1d0c8a3f7e25",
                platform_id="7421538806219533999",
                api_version="tikhub-v1",
            ),
            {"aweme_id": "7421538806219533999", "desc": "عرض الجمعة"},
        ),
    )
    # A backfilled article (found_via sitemap_backfill or commoncrawl) carries job_kind backfill (F-05).
    url = "https://www.example-daily.iq/economy/2026/09/26/fiberx-wasit"
    canonical = url
    hexid = article_key(canonical).split(":", 2)[2]
    valid(
        S,
        "article-backfill",
        msg(
            envelope(
                "news-article-extractor",
                "article",
                "news",
                "green",
                None,
                "2026-10-09T03:00:00Z",
                "01M4F72A8RQ0N3K5D2B7T4W9XC",
                "news_excerpt",
                rawref("green", "news", "2026-10-09", "news-article-extractor", 500, 2),
                source_id="3c7f9d52-1e4a-4b86-a0d3-7b2e5c8f1a90",
                platform_id=hexid,
                job_kind="backfill",
                api_version="extract-v1",
                context={"url_key": url_key(url), "access_mode": "direct"},
            ),
            {
                "url": url,
                "final_url": url,
                "canonical_url": canonical,
                "title": "فايبر اكس في واسط",
                "excerpt": "أعلنت شركة فايبر اكس...",
                "published_at": "2026-09-26T08:00:00Z",
                "text_full_ref": None,
                "text_expires_at": None,
                "text_sha256": None,
                "title_sha256": "c3f60a1d9c7e4825f1a0d3c9b7e65a24d8f1c0b9a7e3d5f21c6b4a0e9d8f7c14",
                "extractor": "trafilatura",
                "extractor_version": "1.12.2",
            },
        ),
    )


def web_result() -> None:
    from listening_contracts.url import canonical_url_hash

    url = "https://forum.example-iq.net/t/fiberx-wasit-outage/4417?utm_source=mojeek"
    canonical = "https://forum.example-iq.net/t/fiberx-wasit-outage/4417"
    valid(
        S,
        "result",
        msg(
            envelope(
                "search-hit-router",
                "result",
                "web",
                "green",
                "mojeek",
                "2026-10-06T03:04:11Z",
                "01M47F78AGDCFWH3S8DKZZJENT",
                "news_excerpt",
                "raw/green/web/2026/10/06/search-hit-router/000012.jsonl.zst#7",
                source_id="7b3e5f8a-1c2d-4e4f-9a6b-7c8d9e0f1a2b",
                platform_id=canonical_url_hash(canonical),
                api_version="search.results/v1",
                provenance_service="web-search-mojeek",
                produced_at="2026-10-06T03:15:02Z",
            ),
            {
                "engine": "mojeek",
                "rank": 3,
                "title": "انقطاع فايبر اكس في الكوت منذ الصباح",
                "url": url,
                "canonical_url": canonical,
                "snippet": "هل عندكم انقطاع؟ النت مقطوع بالكوت من الصبح وفايبر اكس ما ترد",
            },
        ),
    )


def invalids() -> None:
    import json

    from common import ROOT

    base = json.loads((ROOT / S / "valid" / "prd-fb-page-feed-poller.json").read_text())
    comment = json.loads((ROOT / S / "valid" / "prd-ig-own-comments-fetcher.json").read_text())
    article = json.loads((ROOT / S / "valid" / "prd-news-article-extractor.json").read_text())
    reaction = json.loads((ROOT / S / "valid" / "reaction.json").read_text())
    metrics = json.loads((ROOT / S / "valid" / "metrics.json").read_text())
    stream = json.loads((ROOT / S / "valid" / "prd-x-filtered-stream.json").read_text())
    tg = json.loads((ROOT / S / "valid" / "prd-tg-bot-channel-receiver.json").read_text())
    profile = json.loads((ROOT / S / "valid" / "profile.json").read_text())
    resp = json.loads((ROOT / S / "valid" / "search-response.json").read_text())
    yt = json.loads((ROOT / S / "valid" / "prd-yt-keyword-search.json").read_text())
    invalid(
        S,
        "context-partial-one",
        with_(yt, ("envelope", "context", "partial"), 1),
        ["envelope", "context", "partial"],
        "a constant keeps its JSON type: 0 is not false and true is not 1 (finding 6)",
    )
    # A payload's strings and keys are well-formed Unicode too (finding 5).
    invalid(
        S,
        "payload-lone-surrogate",
        with_(base, ("payload", "message"), base["payload"]["message"] + "\ud83d"),
        ["payload", "message"],
        "every string and key is well-formed Unicode (UTF-8 encodable, ADR-0006)",
    )
    invalid(
        S,
        "payload-key-lone-surrogate",
        with_(base, ("payload", "\ud83d"), 1),
        ["payload", "\ud83d"],
        "every string and key is well-formed Unicode (UTF-8 encodable, ADR-0006)",
    )
    for f in ("schema", "message_id", "produced_at", "producer"):
        invalid(
            S,
            f"no-metadata-{f.replace('_', '-')}",
            without(base, "envelope", f),
            ["envelope", f],
            f"every message carries {f} (ADR-0002)",
        )
    invalid(
        S,
        "no-provenance",
        without(base, "envelope", "provenance"),
        ["envelope", "provenance"],
        "a data message carries provenance (ADR-0003)",
    )
    invalid(
        S,
        "no-retention-class",
        without(base, "envelope", "retention_class"),
        ["envelope", "retention_class"],
        "a data message carries retention_class (ADR-0003)",
    )
    invalid(
        S,
        "flat-route",
        with_(base, ("envelope", "route"), "green"),
        ["envelope", "route"],
        "route travels only inside provenance (ADR-0003)",
    )
    invalid(
        S,
        "batch",
        with_(
            base,
            ("envelope", "batch"),
            "raw/green/facebook/2026/10/06/fb-page-feed-poller/000123.jsonl.zst",
        ),
        ["envelope", "batch"],
        "batch gives way to raw_ref (ADR-0005)",
    )
    invalid(
        S,
        "post-without-platform-id",
        without(base, "envelope", "platform_id"),
        ["envelope", "platform_id"],
        "a content kind carries platform_id (ADR-0005)",
    )
    invalid(
        S,
        "post-without-key",
        without(base, "envelope", "idempotency_key"),
        ["envelope", "idempotency_key"],
        "a content kind carries idempotency_key (ADR-0005)",
    )
    invalid(
        S,
        "key-not-the-helpers",
        with_(
            base, ("envelope", "idempotency_key"), "facebook:post:100064583471102_1198837625012735"
        ),
        ["envelope", "idempotency_key"],
        "the key equals the helper's output for the record (ADR-0006)",
    )
    invalid(
        S,
        "comment-without-parent",
        without(comment, "envelope", "parent_id"),
        ["envelope", "parent_id"],
        "a comment carries parent_id (ADR-0009)",
    )
    invalid(
        S,
        "comment-without-root",
        without(comment, "envelope", "root_id"),
        ["envelope", "root_id"],
        "a comment carries root_id (ADR-0009)",
    )
    invalid(
        S,
        "comment-without-author-ref",
        without(comment, "envelope", "author_ref"),
        ["envelope", "author_ref"],
        "a comment carries author_ref, null where the platform gives none (Q3)",
    )
    invalid(
        S,
        "reaction-without-platform-id",
        without(reaction, "envelope", "platform_id"),
        ["envelope", "platform_id"],
        "a reaction is keyed by its event id (F-37)",
    )
    invalid(
        S,
        "reaction-without-author-ref",
        without(reaction, "envelope", "author_ref"),
        ["envelope", "author_ref"],
        "a reaction carries author_ref (Q3)",
    )
    invalid(
        S,
        "metrics-without-item-key",
        with_(metrics, ("envelope", "context"), {}),
        ["envelope", "context", "item_key"],
        "a metrics record names the observed item's key (ADR-0034; F-37)",
    )
    invalid(
        S,
        "source-and-candidate",
        with_(base, ("envelope", "candidate_key"), "facebook:100064583471102"),
        ["envelope", "candidate_key"],
        "a record carries source_id or candidate_key, never both (ADR-0005 L28)",
    )
    invalid(
        S,
        "neither-source-nor-candidate",
        without(profile, "envelope", "candidate_key"),
        ["envelope", "source_id"],
        "a record carries source_id or candidate_key (ADR-0005)",
    )
    invalid(
        S,
        "search-response-neither",
        without(resp, "envelope", "source_id"),
        ["envelope", "source_id"],
        "a search response is keyed by the rule's source_id (ADR-0005)",
    )
    invalid(
        S,
        "undeclared-context-key",
        with_(base, ("envelope", "context"), {"paid": True}),
        ["envelope", "context", "paid"],
        "context holds only its producer's declared keys (ADR-0005)",
    )
    invalid(
        S,
        "unknown-context-key",
        with_(base, ("envelope", "context"), {"metrics_observation": "poll"}),
        ["envelope", "context", "metrics_observation"],
        "context holds only declared keys (ADR-0005)",
    )
    invalid(
        S,
        "stream-without-connection-id",
        with_(stream, ("envelope", "context"), {"paid": True}),
        ["envelope", "context", "connection_id"],
        "a stream record carries its delivery id in context (ADR-0005)",
    )
    invalid(
        S,
        "bot-without-update-id",
        with_(tg, ("envelope", "context"), {}),
        ["envelope", "context", "update_id"],
        "a bot record carries its delivery id in context (ADR-0005)",
    )
    invalid(
        S,
        "partial-false",
        with_(
            json.loads((ROOT / S / "valid" / "prd-yt-pubsub-receiver.json").read_text()),
            ("envelope", "context", "partial"),
            False,
        ),
        ["envelope", "context", "partial"],
        "partial is true when present (ADR-0065)",
    )
    invalid(
        S,
        "unknown-kind",
        with_(base, ("envelope", "kind"), "article_url"),
        ["envelope", "kind"],
        "the record kind is one of ADR-0008's",
    )
    invalid(
        S,
        "reason-as-job-kind",
        with_(base, ("envelope", "job_kind"), "first_run"),
        ["envelope", "job_kind"],
        "job_kind is a job kind, push or stream (ADR-0005, ADR-0011)",
    )
    invalid(
        S,
        "uppercase-route",
        with_(base, ("envelope", "provenance", "route"), "GREEN"),
        ["envelope", "provenance", "route"],
        "routes are lower case (ADR-0070 c))",
    )
    invalid(
        S,
        "vendor-spelling",
        with_(
            json.loads((ROOT / S / "valid" / "prd-tg-channel-posts-poller.json").read_text()),
            ("envelope", "provenance", "vendor"),
            "apify_tugelbay",
        ),
        ["envelope", "provenance", "vendor"],
        "one lower-case vendor spelling, from the registry (ADR-0051 (c))",
    )
    invalid(
        S,
        "amber-without-vendor",
        with_(
            json.loads((ROOT / S / "valid" / "prd-tg-channel-posts-poller.json").read_text()),
            ("envelope", "provenance", "vendor"),
            None,
        ),
        ["envelope", "provenance", "vendor"],
        "an amber record names its vendor (ADR-0051 (c))",
    )
    invalid(
        S,
        "unknown-service",
        with_(base, ("envelope", "producer", "service"), "fb-page-poller"),
        ["envelope", "producer", "service"],
        "producer.service is a service of the index (Q1, F-09)",
    )
    invalid(
        S,
        "resolver-writes-post",
        with_(
            with_(
                with_(profile, ("envelope", "kind"), "post"),
                ("envelope", "platform_id"),
                "17841400112233445",
            ),
            ("envelope", "idempotency_key"),
            key("instagram", "post", "17841400112233445"),
        ),
        ["envelope", "producer", "service"],
        "a raw.items writer writes only its record kinds",
    )
    invalid(
        S,
        "non-utc-fetched-at",
        with_(base, ("envelope", "provenance", "fetched_at"), "2026-10-06T12:15:42+03:00"),
        ["envelope", "provenance", "fetched_at"],
        "message timestamps are UTC with Z",
    )
    invalid(
        S,
        "numeric-platform-id",
        with_(base, ("envelope", "platform_id"), 100064583471102),
        ["envelope", "platform_id"],
        "platform ids are strings, never numbers (ADR-0007)",
    )
    invalid(
        S,
        "prefixed-author-ref",
        with_(comment, ("envelope", "author_ref"), "hmac:8d3f0a6c1e9b4d27a5f1"),
        ["envelope", "author_ref"],
        "author_ref is 64 lower-case hex, no prefix (ADR-0010)",
    )
    invalid(
        S,
        "raw-ref-route-mismatch",
        with_(
            base,
            ("envelope", "raw_ref"),
            "raw/amber/facebook/2026/10/06/fb-page-feed-poller/000123.jsonl.zst#17",
        ),
        ["envelope", "raw_ref"],
        "raw_ref names the record's own route and platform (ADR-0005)",
    )
    invalid(
        S,
        "article-without-extractor",
        without(article, "payload", "extractor"),
        ["payload", "extractor"],
        "an article payload is the typed extract (F-30)",
    )
    invalid(
        S,
        "article-unknown-field",
        with_(article, ("payload", "html"), "<html></html>"),
        ["payload", "html"],
        "the article extract carries only its typed fields (F-30)",
    )
    result = json.loads((ROOT / S / "valid" / "result.json").read_text())
    invalid(
        S,
        "result-key-not-the-helpers",
        with_(result, ("envelope", "idempotency_key"), "web:result:" + "0" * 64),
        ["envelope", "idempotency_key"],
        "a web result's key is web:result:<canonical_url_hash> (ADR-0038)",
    )
    tolerant(S, "unknown-envelope-field", with_(base, ("envelope", "trace_id"), "abc"))
    tolerant(
        S,
        "unknown-article-field",
        with_(article, ("payload", "summary_ai"), "a later optional field"),
    )


def run() -> None:
    facebook()
    instagram()
    linkedin()
    news()
    tiktok()
    telegram()
    x()
    youtube()
    resolvers_and_web()
    web_result()
    invalids()
