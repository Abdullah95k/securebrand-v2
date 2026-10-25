"""Fixtures for the derived data topics: items.normalized, item.hits, discovery.hits,
poster.profiles, items.analysis, item.metrics, deletions, article.urls, search.results,
crawl.policies and news.dedup."""

import json
from typing import Any

from common import (
    CLIENT,
    CLIENT2,
    ROOT,
    content_hash,
    deletion_id,
    hit_id,
    iid,
    invalid,
    key,
    meta,
    metadata_invalids,
    prd,
    prov,
    ref,
    tolerant,
    ulid_for,
    valid,
    with_,
    without,
)

from listening_contracts.keys import (
    analysis_key,
    candidate_key_from_handle,
    candidate_key_from_id,
    facebook_group_candidate_key,
    item_id,
    news_site_candidate_key,
    telegram_post_id,
)
from listening_contracts.ulid import hit_message_id
from listening_contracts.url import article_key, canonical_url_hash, url_hash, url_key

R_META = "schema, message_id, produced_at and producer stamped by the SDK (ADR-0002)"
R_PROV = "route, vendor, service and fetched_at fold into provenance (ADR-0003)"

# The post of normalize-item's example, analysed and matched downstream.
FB_SOURCE = "a3c0f1e2-5b6d-4c7e-9f80-112233445566"
FB_POST = "1234567890_9876543210"
FB_ITEM = iid("facebook", "post", FB_POST)
FB_TEXT = "النت منقطع بالبصرة من الصبح، شنو السالفة؟"
FB_PROV = prov("green", None, "fb-page-feed-poller", "2026-10-06T09:13:58Z")
KSV = "cs:3f9a1c0d7e2b4a6c8e0f1a3b5c7d9e1f2a4b6c8d0e2f4a6b8c0d2e4f6a8b0c2d"


def normalized() -> None:
    s = "items.normalized/v1"
    base: dict[str, Any] = {
        **meta(s, "normalize-item", "01J9N2Q7Z4T8X1V6M3K0H5R2WB", "2026-10-06T09:14:03Z", "1.4.0"),
        "item_id": FB_ITEM,
        "idempotency_key": key("facebook", "post", FB_POST),
        "platform": "facebook",
        "kind": "post",
        "source_id": FB_SOURCE,
        "parent_id": None,
        "root_id": None,
        "parent_seen": True,
        "content_hash": content_hash(None, FB_TEXT),
        "version": 1,
        "platform_id": FB_POST,
        "url": "https://www.facebook.com/1234567890/posts/9876543210",
        "created_at": "2026-10-06T08:51:40Z",
        "title": None,
        "text": FB_TEXT,
        "text_norm": "النت منقطع بالبصره من الصبح شنو السالفه",
        "lang": "ar",
        "lang_conf": 0.98,
        "dialect": "iraqi",
        "dialect_conf": 0.84,
        "script": "arab",
        "lang_model_version": "lid-iq-2026.09",
        "lang_pending": False,
        "author": {
            "author_ref": ref("1234567890", "facebook"),
            "author_type": "source",
            "author_source_id": FB_SOURCE,
            "display_name": "Example Page",
        },
        "media": [{"type": "image", "url": "https://scontent.example/abc.jpg"}],
        "hashtags": [],
        "at_mentions": [],
        "links": [],
        "metrics_snapshot": {
            "views": None,
            "likes": 120,
            "comments": 14,
            "shares": 3,
            "reactions_by_type": {"like": 100, "love": 20},
        },
        "expires_at": None,
        "normalizer_version": "1.4.0",
        "raw_ref": "raw/green/facebook/2026/10/06/fb-page-feed-poller/000007.jsonl.zst#1532",
        "job_kind": "rotation",
        "sensitive_event": False,
        "client_ids": [CLIENT],
        "provenance": FB_PROV,
        "retention_class": "meta_on_request",
    }
    valid(s, "prd-normalize-item", base)
    prd(
        "normalize-item",
        "docs/prds/shared/normalize-item.md",
        93,
        s,
        "prd-normalize-item",
        [
            R_PROV,
            "reactions_by_type keys in lower case, as item.metrics defines them (F-34)",
            "author_ref takes the helper's 64-hex form (ADR-0010); content_hash computed with the helper (ADR-0009)",
            "views null where the platform gives none (ADR-0034)",
            "raw_ref batch written with six digits (ADR-0005)",
            "job_kind, lang_pending and sensitive_event added (ADR-0005, ADR-0070 d), ADR-0059); client_ids copied from the raw envelope (O-10)",
        ],
    )
    post_key = key("youtube", "video", "q3Vt8LmZ2xA")
    comment: dict[str, Any] = {
        **base,
        **meta(
            s,
            "normalize-item",
            "01J9P4D2K8W6Y3N0Q5T7V1X9ZC",
            "2026-10-07T07:03:20Z",
            "1.4.0",
            "comment",
        ),
        "item_id": iid("youtube", "comment", "UgzK7pQ2mV9xR4tL1bN6AaABAg"),
        "idempotency_key": key("youtube", "comment", "UgzK7pQ2mV9xR4tL1bN6AaABAg"),
        "platform": "youtube",
        "kind": "comment",
        "source_id": "3a9e5c1d-7f2b-4e8a-b6d0-91c4f2e7a835",
        "parent_id": item_id(post_key),
        "root_id": item_id(post_key),
        "content_hash": content_hash(None, "حلو الفيديو"),
        "platform_id": "UgzK7pQ2mV9xR4tL1bN6AaABAg",
        "url": None,
        "created_at": "2026-10-07T06:40:00Z",
        "text": "حلو الفيديو",
        "text_norm": "حلو الفيديو",
        "author": {
            "author_ref": ref("UCaaaaaaaaaaaaaaaaaaaaaa", "youtube"),
            "author_type": "individual",
            "author_source_id": None,
        },
        "media": [],
        "metrics_snapshot": {
            "views": None,
            "likes": 3,
            "comments": None,
            "shares": None,
            "reactions_by_type": None,
        },
        "raw_ref": "raw/green/youtube/2026/10/07/yt-comments-fetcher/000057.jsonl.zst#1",
        "job_kind": "comments",
        "video_channel_id": "UC7xQe2lW9pK3bN5aV1rT8sQ",
        "provenance": prov("green", None, "yt-comments-fetcher", "2026-10-07T07:03:11Z"),
        "retention_class": "youtube_30d_text",
    }
    valid(s, "comment-youtube", comment)
    hexid = article_key("https://www.example-daily.iq/politics/2026/10/06/budget-session").split(
        ":", 2
    )[2]
    article: dict[str, Any] = {
        **base,
        **meta(
            s,
            "normalize-item",
            "01J9N3A4K8R2T7V5X0M6C1D9HE",
            "2026-10-06T05:52:40Z",
            "1.4.0",
            "article",
        ),
        "item_id": iid("news", "article", hexid),
        "idempotency_key": key("news", "article", hexid),
        "platform": "news",
        "kind": "article",
        "source_id": "3c7f9d52-1e4a-4b86-a0d3-7b2e5c8f1a90",
        "platform_id": hexid,
        "url": "https://www.example-daily.iq/politics/2026/10/06/budget-session",
        "created_at": "2026-10-06T05:41:00Z",
        "title": "البرلمان يحدد موعد جلسة الموازنة",
        "text": "حدد مجلس النواب يوم الأحد المقبل موعدا لعقد جلسة مخصصة لمناقشة مشروع قانون الموازنة الاتحادية",
        "text_norm": "حدد مجلس النواب يوم الاحد المقبل موعدا لعقد جلسه مخصصه لمناقشه مشروع قانون الموازنه الاتحاديه",
        "content_hash": content_hash(
            "البرلمان يحدد موعد جلسة الموازنة",
            "حدد مجلس النواب يوم الأحد المقبل موعدا لعقد جلسة مخصصة لمناقشة مشروع قانون الموازنة الاتحادية",
        ),
        "author": {
            "author_ref": None,
            "author_type": "source",
            "author_source_id": "3c7f9d52-1e4a-4b86-a0d3-7b2e5c8f1a90",
            "display_name": "Example Daily",
        },
        "media": [],
        "metrics_snapshot": {
            "views": None,
            "likes": None,
            "comments": None,
            "shares": None,
            "reactions_by_type": None,
        },
        "raw_ref": "raw/green/news/2026/10/06/news-article-extractor/000412.jsonl.zst#20",
        "text_full_ref": f"cache/news/2026/10/06/{hexid}.json.zst",
        "usage_signals": {"search": "yes", "ai_input": "unset", "ai_train": "no"},
        "provenance": prov("green", None, "news-article-extractor", "2026-10-06T05:52:30Z"),
        "retention_class": "news_excerpt",
    }
    valid(s, "article", article)
    vtitle, vtext = "انقطاع الانترنت في البصرة", "تقرير عن انقطاع الانترنت في البصرة اليوم"
    video = {
        **base,
        **meta(
            s,
            "normalize-item",
            "01J9N2Q7Z4T8X1V6M3K0H5R2WC",
            "2026-10-06T03:05:00Z",
            "1.4.0",
            "video",
        ),
        "item_id": iid("youtube", "video", "dQw4w9WgXcQ"),
        "idempotency_key": key("youtube", "video", "dQw4w9WgXcQ"),
        "platform": "youtube",
        "kind": "video",
        "source_id": "7d2b0c4e-1f3a-4b5c-8d6e-9f0a1b2c3d4e",
        "platform_id": "dQw4w9WgXcQ",
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "created_at": "2026-10-06T02:40:00Z",
        "title": vtitle,
        "text": vtext,
        "text_norm": vtext,
        "content_hash": content_hash(vtitle, vtext),
        "author": {
            "author_ref": None,
            "author_type": "source",
            "author_source_id": "2b7d4e90-1c3a-4f6e-8d25-7a9b0c1e3f42",
            "display_name": "قناة المثال",
            "author_followers": 412000,
        },
        "media": [{"type": "video", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}],
        "metrics_snapshot": {
            "views": 48213,
            "likes": 1904,
            "comments": 377,
            "shares": None,
            "reactions_by_type": None,
        },
        "raw_ref": "raw/green/youtube/2026/10/06/yt-video-details-fetcher/000031.jsonl.zst#4",
        "job_kind": "first_sight",
        "video_channel_id": "UCq3Ov8nVbT0xY1zKp2LmA4w",
        "client_ids": [CLIENT],
        "provenance": prov("green", None, "yt-video-details-fetcher", "2026-10-06T03:04:50Z"),
        "retention_class": "youtube_30d_text",
    }
    valid(s, "video-youtube", video)
    canonical = "https://forum.example-iq.net/t/fiberx-wasit-outage/4417"
    rhex = canonical_url_hash(canonical)
    rtitle, rtext = (
        "انقطاع فايبر اكس في الكوت منذ الصباح",
        "هل عندكم انقطاع؟ النت مقطوع بالكوت من الصبح وفايبر اكس ما ترد",
    )
    result = {
        **base,
        **meta(
            s,
            "normalize-item",
            "01J9N2Q7Z4T8X1V6M3K0H5R2WD",
            "2026-10-06T03:15:10Z",
            "1.4.0",
            "result",
        ),
        "item_id": iid("web", "result", rhex),
        "idempotency_key": key("web", "result", rhex),
        "platform": "web",
        "kind": "result",
        "source_id": "7b3e5f8a-1c2d-4e4f-9a6b-7c8d9e0f1a2b",
        "platform_id": rhex,
        "url": canonical,
        "created_at": None,
        "title": rtitle,
        "text": rtext,
        "text_norm": rtext,
        "content_hash": content_hash(rtitle, rtext),
        "author": {"author_ref": None, "author_type": "individual", "author_source_id": None},
        "media": [],
        "metrics_snapshot": {
            "views": None,
            "likes": None,
            "comments": None,
            "shares": None,
            "reactions_by_type": None,
        },
        "raw_ref": "raw/green/web/2026/10/06/search-hit-router/000012.jsonl.zst#7",
        "job_kind": "rotation",
        "client_ids": [CLIENT],
        "provenance": prov("green", "mojeek", "web-search-mojeek", "2026-10-06T03:04:11Z"),
        "retention_class": "news_excerpt",
    }
    valid(s, "result-web", result)
    invalid(
        s,
        "video-with-parent",
        with_(video, ("parent_id",), FB_ITEM),
        ["parent_id"],
        "a video is a top-level item (ADR-0008)",
    )
    invalid(
        s,
        "article-without-title",
        without(article, "title"),
        ["title"],
        "title is present, null where an item has none",
    )
    invalid(
        s,
        "result-with-root",
        with_(result, ("root_id",), FB_ITEM),
        ["root_id"],
        "a web result is a top-level item (ADR-0038)",
    )
    poster = with_(
        with_(
            base,
            ("author",),
            {"author_ref": None, "author_type": "individual", "author_source_id": None},
        ),
        ("poster_platform_id",),
        "100079876543210",
    )
    valid(s, "post-poster-not-yet-classed", poster)
    invalid(
        s,
        "followers-without-source",
        with_(poster, ("author", "author_followers"), 1200),
        ["author", "author_followers"],
        "author_followers only for a registered source (ADR-0070 d))",
    )
    invalid(
        s,
        "display-name-without-source",
        with_(poster, ("author", "display_name"), "Abu Ali"),
        ["author", "display_name"],
        "display_name only for a registered source (ADR-0010)",
    )
    invalid(
        s,
        "poster-id-with-source",
        with_(base, ("poster_platform_id",), "1234567890"),
        ["poster_platform_id"],
        "poster_platform_id never beside author_source_id (ADR-0031)",
    )
    invalid(
        s,
        "comment-without-parent",
        with_(comment, ("parent_id",), None),
        ["parent_id"],
        "a comment carries parent_id (ADR-0009)",
    )
    invalid(
        s,
        "post-with-parent",
        with_(base, ("parent_id",), FB_ITEM),
        ["parent_id"],
        "a top-level item has no parent (ADR-0008)",
    )
    invalid(
        s,
        "key-not-the-helpers",
        with_(base, ("idempotency_key",), "facebook:post:1234567890_9876543211"),
        ["idempotency_key"],
        "the key equals the helper's output (ADR-0006)",
    )
    invalid(
        s,
        "item-id-not-the-keys",
        with_(base, ("item_id",), "6f1d2c3e-9a4b-5c6d-8e7f-0a1b2c3d4e5f"),
        ["item_id"],
        "item_id = uuid_v5(ns_items, key) (ADR-0006)",
    )
    invalid(
        s,
        "source-type-without-source-id",
        with_(base, ("author", "author_source_id"), None),
        ["author", "author_source_id"],
        "author_type source names its registered source (ADR-0010)",
    )
    invalid(
        s,
        "uppercase-reaction",
        with_(base, ("metrics_snapshot", "reactions_by_type"), {"LIKE": 100}),
        ["metrics_snapshot", "reactions_by_type", "LIKE"],
        "reaction types in lower case (F-34)",
    )
    invalid(
        s,
        "flat-fetched-at",
        with_(base, ("fetched_at",), "2026-10-06T09:13:58Z"),
        ["fetched_at"],
        "fetched_at travels in provenance (ADR-0003)",
    )
    invalid(
        s,
        "no-lang-pending",
        without(base, "lang_pending"),
        ["lang_pending"],
        "lang_pending is required (ADR-0070 d))",
    )
    invalid(
        s,
        "no-provenance",
        without(base, "provenance"),
        ["provenance"],
        "a data message carries provenance (ADR-0003)",
    )
    for f in ("schema", "message_id", "produced_at", "producer"):
        invalid(
            s,
            f"no-metadata-{f.replace('_', '-')}",
            without(base, f),
            [f],
            f"every message carries {f} (ADR-0002)",
        )
    tolerant(s, "unknown-field", with_(base, ("story_id",), "01J9N4W6C2R8T5K1V7X3M0DPZA"))


def hits() -> None:
    s = "item.hits/v1"
    x_post = "1843201122334455667"
    item = iid("x", "post", x_post)
    kw, client, rule = (
        "9a8b7c6d-5e4f-4321-a0b9-c8d7e6f5a4b3",
        CLIENT2,
        "c41b7a90-3d2e-4f5a-8b6c-7d8e9f0a1b2c",
    )
    hid = hit_id(item, client, kw)
    hit_at = "2026-10-06T08:51:40Z"
    base: dict[str, Any] = {
        **meta(s, "keyword-matcher", "01M4871WM0NJ5SWYGET3ZGFGSP", "2026-10-06T09:14:41Z"),
        "hit_id": hid,
        "status": "active",
        "item_id": item,
        "item_version": 1,
        "platform": "x",
        "kind": "post",
        "source_id": rule,
        "client_id": client,
        "keyword_id": kw,
        "keyword_set_version": KSV,
        "lang_model_version": "lid-iq-2026.09",
        "matched_by": "text",
        "matched_term": "زين العراق",
        "form_id": "f2",
        "occurrences": 1,
        "offsets": [[5, 15]],
        "offsets_in": "text_norm",
        "hit_at": hit_at,
        "url": f"https://x.com/i/status/{x_post}",
        "poster": {
            "author_ref": ref("1000000000000000001", "x"),
            "author_type": "individual",
            "author_source_id": None,
        },
        "raw_ref": "raw/green/x/2026/10/06/x-recent-search/000042.jsonl.zst#310",
        "expires_at": None,
        "provenance": prov("green", None, "x-recent-search", "2026-10-06T09:15:04Z"),
        "retention_class": "x_24h_sync",
    }
    base["message_id"] = hit_message_id(hit_at, hid, 1, KSV)
    valid(s, "prd-keyword-matcher", base)
    prd(
        "keyword-matcher",
        "docs/prds/shared/keyword-matcher.md",
        97,
        s,
        "prd-keyword-matcher",
        [
            "the example is the discovery.hits form; an item.hits message is identical except that candidate and candidate_pending give way to poster (§6.2 L119)",
            R_PROV,
            "hit_id from the helper, uuid v5 under ns_hits; message_id the deterministic ULID of (hit_at; hit_id, item_version, keyword_set_version) (ADR-0006)",
            "keyword_set_version written in full, cs:<64 hex> (ADR-0070 a))",
            "matched_by text added (ADR-0031; F-20)",
            "raw_ref batch with six digits",
            "the poster's handle and id replaced by invented ones (D-8)",
        ],
        note="its discovery.hits example is under discovery.hits/v1",
    )
    src_hit: dict[str, Any] = {
        **base,
        "matched_by": "source",
        "matched_term": None,
        "form_id": None,
        "occurrences": 0,
        "offsets": [],
        "offsets_in": None,
    }
    valid(s, "source-match", src_hit)
    yt_item = iid("youtube", "video", "dQw4w9WgXcQ")
    yt: dict[str, Any] = {
        **base,
        "item_id": yt_item,
        "platform": "youtube",
        "kind": "video",
        "hit_id": hit_id(yt_item, client, kw),
        "video_channel_id": "UCuAXFkgsw1L7xaCfnd5JJOw",
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "raw_ref": "raw/green/youtube/2026/10/06/yt-keyword-search/000003.jsonl.zst#12",
        "provenance": prov("green", None, "yt-keyword-search", "2026-10-06T03:04:11Z"),
        "retention_class": "youtube_30d_text",
    }
    yt["message_id"] = hit_message_id(hit_at, yt["hit_id"], 1, KSV)
    valid(s, "video-youtube", yt)
    metadata_invalids(s, base)
    invalid(
        s,
        "text-without-term",
        with_(base, ("matched_term",), None),
        ["matched_term"],
        "a text match carries its term (F-20)",
    )
    invalid(
        s,
        "matched-term-lone-surrogate",
        with_(base, ("matched_term",), base["matched_term"] + "\ud83d"),
        ["matched_term"],
        "every string and key is well-formed Unicode (UTF-8 encodable, ADR-0006)",
    )
    invalid(
        s,
        "source-with-offsets",
        with_(src_hit, ("offsets",), [[1, 2]]),
        ["offsets"],
        "a source match carries no offsets (F-20)",
    )
    invalid(
        s,
        "source-with-occurrences",
        with_(src_hit, ("occurrences",), 1),
        ["occurrences"],
        "a source match has zero occurrences (F-20)",
    )
    invalid(
        s,
        "hit-id-not-the-helpers",
        with_(base, ("hit_id",), "b7e1c9d4-2a53-5f08-9c61-3d4e5f6a7b8c"),
        ["hit_id"],
        "hit_id = uuid_v5(ns_hits, item:client:keyword) (ADR-0006)",
    )
    invalid(
        s,
        "message-id-not-replay-stable",
        with_(base, ("message_id",), "01M486JMB0K5QZM1RWBPZ5NJ95"),
        ["message_id"],
        "a hit's message_id is the deterministic ULID (ADR-0006)",
    )
    invalid(
        s,
        "short-keyword-set-version",
        with_(base, ("keyword_set_version",), "cs:3f9a1c"),
        ["keyword_set_version"],
        "cs:<64 hex> (ADR-0070 a))",
    )
    invalid(
        s,
        "candidate-on-hit",
        with_(base, ("candidate",), {"candidate_key": "x:1234567890"}),
        ["candidate"],
        "item.hits carries poster, never candidate (ADR-0031)",
    )
    invalid(
        s,
        "poster-handle",
        with_(base, ("poster", "handle"), "example_poster_x"),
        ["poster", "handle"],
        "no person's handle on a hit (ADR-0010)",
    )
    invalid(
        s,
        "retracted-unknown-status",
        with_(base, ("status",), "deleted"),
        ["status"],
        "status active or retracted",
    )
    invalid(
        s,
        "not-keyword-matcher",
        with_(
            with_(base, ("producer", "service"), "x-recent-search"),
            ("message_id",),
            base["message_id"],
        ),
        ["producer", "service"],
        "keyword-matcher alone writes item.hits (ADR-0031)",
    )
    tolerant(s, "unknown-field", with_(base, ("matched_text",), "زين العراق"))


def discovery() -> None:
    s = "discovery.hits/v1"
    x_post = "1843201122334455667"
    rule, kw = "c41b7a90-3d2e-4f5a-8b6c-7d8e9f0a1b2c", "9a8b7c6d-5e4f-4321-a0b9-c8d7e6f5a4b3"
    hit_at = "2026-10-06T08:51:40Z"
    item = iid("x", "post", x_post)
    km: dict[str, Any] = {
        **meta(s, "keyword-matcher", "01M4871WM0NJ5SWYGET3ZGFGSP", "2026-10-06T09:14:41Z"),
        "candidate": {
            "candidate_key": "x:1000000000000000001",
            "platform": "x",
            "type": None,
            "platform_id": "1000000000000000001",
            "handle": "example_poster_x",
            "url": None,
        },
        "evidence_type": "keyword_hit",
        "item_id": item,
        "url": None,
        "source_id": rule,
        "keyword_ids": [kw],
        "client_ids": [CLIENT2],
        "hit_at": hit_at,
        "evidence": {
            "hit_id": hit_id(item, CLIENT2, kw),
            "matched_term": "زين العراق",
            "form_id": "f2",
            "keyword_set_version": KSV,
        },
        "provenance": prov("green", None, "x-recent-search", "2026-10-06T09:15:04Z"),
        "retention_class": "x_24h_sync",
    }
    valid(s, "prd-keyword-matcher", km)
    prd(
        "keyword-matcher",
        "docs/prds/shared/keyword-matcher.md",
        97,
        s,
        "prd-keyword-matcher",
        [
            R_PROV,
            "the hit's own fields go: hit_id, matched_term, form_id and keyword_set_version move into the keyword_hit evidence; status, item_version, kind, offsets, occurrences and raw_ref go (ADR-0031)",
            "client_id and keyword_id become client_ids and keyword_ids (ADR-0031)",
            "candidate.author_ref and candidate_pending go: the candidate carries the poster's clear id until poster-resolver classes it (ADR-0010 L49, ADR-0031)",
            "candidate.type null: keyword-matcher cannot tell the poster kind",
            "item_id names the item, url null (exactly one)",
            "the poster's handle and id replaced by invented ones (D-8)",
        ],
    )
    fb: dict[str, Any] = {
        **meta(s, "fb-page-search", "01M47YF7J0TMKPRYDBNVW3319Z", "2026-10-06T06:30:13Z"),
        "candidate": {
            "candidate_key": "facebook:104557812990341",
            "platform": "facebook",
            "type": "page",
            "platform_id": "104557812990341",
            "handle": None,
            "url": "https://www.facebook.com/profile.php?id=104557812990341",
        },
        "evidence_type": "page_search",
        "item_id": None,
        "url": "https://www.facebook.com/profile.php?id=104557812990341",
        "source_id": "5c0e8a24-7b1d-4f39-a6e2-9d3c1b7f0a58",
        "keyword_ids": ["3d9c1b2a-7e4f-4a6b-8c1d-2e5f6a7b8c9d"],
        "client_ids": [CLIENT],
        "hit_at": "2026-10-06T06:30:12Z",
        "evidence": {
            "query": "زين العراق",
            "name": "زين العراق - فرع البصرة",
            "is_verified": False,
            "location": {"city": "Basra", "country": "Iraq"},
        },
        "provenance": prov("green", None, "fb-page-search", "2026-10-06T06:30:12Z"),
        "retention_class": "meta_on_request",
    }
    valid(s, "prd-fb-page-search", fb)
    prd(
        "fb-page-search",
        "docs/prds/facebook/fb-page-search.md",
        95,
        s,
        "prd-fb-page-search",
        [
            R_META,
            R_PROV,
            "hit_type and context go; found_at becomes hit_at (ADR-0031)",
            "keyword_id becomes keyword_ids; source_id is the keyword-rule row (ADR-0004, ADR-0044)",
            "the candidate takes ADR-0031's shape; name, is_verified, location and the query move into the page_search evidence",
            "url names the page found (exactly one of item_id and url)",
        ],
    )
    tg_post = telegram_post_id("basra_prices", "18231")
    tg: dict[str, Any] = {
        **meta(s, "tg-message-search", "01M486Z3M0TQ5KX8D2N6C4B0RW", "2026-10-06T03:12:46Z"),
        "candidate": {
            "candidate_key": candidate_key_from_handle("telegram", "basra_prices"),
            "platform": "telegram",
            "type": "channel",
            "platform_id": "basra_prices",
            "handle": "basra_prices",
            "url": "https://t.me/basra_prices",
        },
        "evidence_type": "early_signal",
        "item_id": iid("telegram", "post", tg_post),
        "url": None,
        "source_id": "2e8f4b61-0c7a-4d93-b5e1-6a2c9f0d8b47",
        "keyword_ids": ["c6f2f07f-9f2c-48b8-a5bf-b265fdb569d1"],
        "client_ids": ["c7f12d45-b7c5-467d-aa82-e7826ed8abf2"],
        "hit_at": "2026-10-06T03:12:44Z",
        "evidence": {"display_name": "أسعار البصرة", "lang": "ar"},
        "provenance": prov("amber", "telemetrio", "tg-message-search", "2026-10-06T03:12:44Z"),
        "retention_class": "vendor_agreed",
    }
    valid(s, "prd-tg-message-search", tg)
    prd(
        "tg-message-search",
        "docs/prds/telegram/tg-message-search.md",
        77,
        s,
        "prd-tg-message-search",
        [
            R_META,
            R_PROV,
            "the item key gives way to item_id; kind goes (ADR-0031)",
            "poster becomes the candidate; display_name moves into the early_signal evidence",
            "source_id added: the keyword-rule row that produced the find (ADR-0004)",
            "hit_at added",
        ],
    )
    shr: dict[str, Any] = {
        **meta(s, "search-hit-router", "01M47K8B60RM3M56CMJWGZ9C6G", "2026-10-06T03:15:02Z"),
        "candidate": {
            "candidate_key": candidate_key_from_handle("instagram", "example_creator_iq"),
            "platform": "instagram",
            "type": "account",
            "platform_id": None,
            "handle": "example_creator_iq",
            "url": "https://www.instagram.com/example_creator_iq/",
        },
        "evidence_type": "web_search",
        "item_id": None,
        "url": "https://www.instagram.com/example_creator_iq/reel/Cx4kQ2LsT9m/",
        "source_id": "7d2b0c4e-1f3a-4b5c-8d6e-9f0a1b2c3d4e",
        "keyword_ids": ["0cd402b6-9015-45f8-86b4-d90cc086d320"],
        "client_ids": [CLIENT],
        "hit_at": "2026-10-06T03:14:09Z",
        "evidence": {
            "canonical_url_hash": canonical_url_hash(
                "https://www.instagram.com/example_creator_iq/reel/Cx4kQ2LsT9m/"
            ),
            "engines": ["perplexity", "mojeek"],
            "sightings": 3,
            "first_seen_at": "2026-10-05T03:14:09Z",
            "title": "…",
            "snippet": "…",
        },
        "provenance": prov("green", "perplexity", "web-search-perplexity", "2026-10-06T03:14:08Z"),
        "retention_class": "news_excerpt",
    }
    valid(s, "prd-search-hit-router", shr)
    prd(
        "search-hit-router",
        "docs/prds/web/search-hit-router.md",
        101,
        s,
        "prd-search-hit-router",
        [
            R_PROV,
            "the provenance is the engine's that fetched the result (ADR-0003 L25)",
            "type, platform and poster_ref give way to the candidate block; origin goes (ADR-0031)",
            "keyword_rule_ids become the rule's source_id; client_ids move to the top (ADR-0031)",
            "canonical_url_hash bare hex from the one normaliser (ADR-0036; Q9)",
            "url names the result (exactly one of item_id and url)",
        ],
    )
    cc: dict[str, Any] = {
        **meta(s, "web-commoncrawl-scanner", "01M4F71ZR0Q8N3K5D2B7T4W9XC", "2026-10-09T02:14:55Z"),
        "candidate": {
            "candidate_key": news_site_candidate_key("example-daily.iq"),
            "platform": "news",
            "type": "site",
            "platform_id": None,
            "handle": None,
            "url": "https://www.example-daily.iq/",
        },
        "evidence_type": "commoncrawl",
        "item_id": None,
        "url": "https://www.example-daily.iq/",
        "source_id": None,
        "keyword_ids": [],
        "client_ids": [],
        "hit_at": "2026-10-09T02:14:50Z",
        "evidence": {
            "crawl_id": "CC-MAIN-2026-38",
            "captures": 1840,
            "first_capture": "2026-09-14",
            "last_capture": "2026-09-27",
            "sample_urls": ["https://www.example-daily.iq/economy/2026/09/26/fiberx-wasit"],
            "path_signals": ["date_path", "news_path"],
            "language_share": {"ara": 0.93},
            "news_score": 0.82,
        },
        "provenance": prov("green", None, "web-commoncrawl-scanner", "2026-10-09T02:14:50Z"),
        "retention_class": "news_excerpt",
    }
    valid(s, "prd-web-commoncrawl-scanner", cc)
    prd(
        "web-commoncrawl-scanner",
        "docs/prds/web/web-commoncrawl-scanner.md",
        86,
        s,
        "prd-web-commoncrawl-scanner",
        [
            R_PROV,
            "the key news:<domain> becomes news:site:<registrable domain> (ADR-0032, ADR-0037)",
            "type, platform and poster_ref give way to the candidate block; origin and keyword_rule_id go (ADR-0031)",
            "source_id null: the scan has no producing source (F-31)",
            "url names the site (exactly one of item_id and url)",
        ],
    )
    # The group of fb-keyword-search's PRD post, named in its raw record's context (ADR-0031 L34).
    group = {
        **km,
        "candidate": {
            "candidate_key": facebook_group_candidate_key("271936048205533"),
            "platform": "facebook",
            "type": "group",
            "platform_id": "271936048205533",
            "handle": None,
            "url": None,
        },
        "evidence_type": "container",
        "item_id": iid("facebook", "post", "4118203958217764"),
        "evidence": {"name": "مجموعة أهالي المنطقة"},
        "source_id": "c7e41b95-0a3d-4f82-b6c9-18d5e2a07f43",
        "provenance": prov("amber", "sociavault", "fb-keyword-search", "2026-10-06T03:12:48Z"),
        "retention_class": "vendor_agreed",
    }
    valid(s, "container-group", group)
    xr = {
        **km,
        **meta(s, "x-recent-search", "01M487XBH07GQE33JRM29CMCMZ", "2026-10-06T09:15:06Z"),
        "candidate": {
            "candidate_key": "x:1000000000000000001",
            "platform": "x",
            "type": "account",
            "platform_id": "1000000000000000001",
            "handle": "example_poster_x",
            "url": None,
        },
        "evidence_type": "early_signal",
        "source_id": "7c1d9a2e-55b4-4f1e-8a0c-3e9f6b2d4a71",
        "keyword_ids": ["0b6b8c7e-0000-4e0f-9c3a-5f2d1e8a7b61"],
        "client_ids": [CLIENT],
        "evidence": {
            "matched_terms": ["دجلة تيليكوم"],
            "lang": "ar",
            "public_metrics": {
                "retweet_count": 2,
                "reply_count": 5,
                "like_count": 38,
                "quote_count": 1,
            },
        },
    }
    valid(s, "early-signal-x", xr)
    metadata_invalids(s, km)
    invalid(
        s,
        "item-id-and-url",
        with_(km, ("url",), "https://x.com/i/status/1843201122334455667"),
        ["url"],
        "exactly one of item_id and url (ADR-0031)",
    )
    invalid(
        s,
        "neither-item-nor-url",
        with_(km, ("item_id",), None),
        ["item_id"],
        "exactly one of item_id and url (ADR-0031)",
    )
    invalid(
        s,
        "no-source-outside-commoncrawl",
        with_(km, ("source_id",), None),
        ["source_id"],
        "only web-commoncrawl-scanner's hit has no producing source (F-31)",
    )
    invalid(
        s,
        "old-news-key",
        with_(cc, ("candidate", "candidate_key"), "news:example-daily.iq"),
        ["candidate", "candidate_key"],
        "a site is news:site:<registrable domain> (ADR-0032)",
    )
    invalid(
        s,
        "post-key-as-candidate",
        with_(km, ("candidate", "candidate_key"), "instagram:post:Cx4kQ2LsT9m"),
        ["candidate", "candidate_key"],
        "a candidate key takes one of the four forms (ADR-0032)",
    )
    invalid(
        s,
        "candidate-platform-mismatch",
        with_(km, ("candidate", "platform"), "instagram"),
        ["candidate", "platform"],
        "the candidate's platform is its key's",
    )
    invalid(
        s,
        "evidence-of-another-type",
        with_(km, ("evidence", "sightings"), 3),
        ["evidence", "sightings"],
        "each evidence block holds its type's keys only (Q8)",
    )
    invalid(
        s,
        "poster-field",
        with_(km, ("poster",), {"handle": "example_poster_x"}),
        ["poster"],
        "poster goes (ADR-0031)",
    )
    invalid(
        s,
        "singular-keyword-id",
        with_(km, ("keyword_id",), kw),
        ["keyword_id"],
        "keyword_ids, never keyword_id (ADR-0031)",
    )
    invalid(
        s,
        "unknown-evidence-type",
        with_(km, ("evidence_type",), "hashtag"),
        ["evidence_type"],
        "evidence_type is one of ADR-0031's",
    )
    invalid(
        s,
        "container-with-hit-evidence",
        with_(group, ("evidence", "matched_term"), "سوق المنصور"),
        ["evidence", "matched_term"],
        "each evidence block holds its type's keys only (Q8)",
    )
    invalid(
        s,
        "early-signal-with-hit-id",
        with_(tg, ("evidence", "hit_id"), "b7e1c9d4-2a53-5f08-9c61-3d4e5f6a7b8c"),
        ["evidence", "hit_id"],
        "each evidence block holds its type's keys only (Q8)",
    )
    invalid(
        s,
        "page-search-empty-query",
        with_(fb, ("evidence", "query"), ""),
        ["evidence", "query"],
        "a page search names its query",
    )
    invalid(
        s,
        "web-search-prefixed-hash",
        with_(
            shr,
            ("evidence", "canonical_url_hash"),
            "sha256:" + shr["evidence"]["canonical_url_hash"],
        ),
        ["evidence", "canonical_url_hash"],
        "canonical_url_hash is bare hex (ADR-0036)",
    )
    invalid(
        s,
        "camel-case-metric",
        with_(xr, ("evidence", "public_metrics"), {"retweetCount": 2}),
        ["evidence", "public_metrics", "retweetCount"],
        "metric names are snake_case (Q8)",
    )
    invalid(
        s,
        "uppercase-language",
        with_(cc, ("evidence", "language_share"), {"ARA": 0.93}),
        ["evidence", "language_share", "ARA"],
        "language keys are snake_case (Q8)",
    )
    tolerant(s, "unknown-evidence-key", with_(shr, ("evidence", "domain_rank"), 4))


def profiles() -> None:
    s = "poster.profiles/v1"

    def signals(**on: Any) -> dict[str, Any]:
        out: dict[str, Any] = {
            k: False
            for k in (
                "iraqi_place",
                "platform_country_iq",
                "phone_964",
                "iq_domain",
                "outlet_link",
                "seed_list",
            )
        }
        evidence = on.pop("evidence", [])
        out.update(on)
        out["signal_evidence"] = evidence
        return out

    def share(
        ar: float = 0,
        ckb: float = 0,
        en: float = 0,
        ar_iraqi: float = 0,
        sample: int = 20,
        mixed: float = 0,
        other: float = 0,
        und: float = 0,
    ) -> dict[str, Any]:
        return {
            "ar": ar,
            "ckb": ckb,
            "en": en,
            "mixed": mixed,
            "other": other,
            "und": und,
            "ar_iraqi": ar_iraqi,
            "sample": sample,
        }

    def full(
        service: str,
        job: str,
        at: str,
        cand: str,
        platform: str,
        route: str,
        vendor: str | None,
        rclass: str,
        **fields: Any,
    ) -> dict[str, Any]:
        msg: dict[str, Any] = {
            **meta(s, service, job, fields.pop("produced_at", at)),
            "platform": platform,
            "status": "resolved",
            "reason": None,
            "followers": None,
            "verified": None,
            "client_ids": [CLIENT],
            "resolved_at": at,
            "cached": False,
            "cached_until": None,
            "candidate_key": cand,
            "source_id": None,
            "source_type": None,
            "account_type": None,
            "individual": None,
            "public_account": None,
            "platform_id": None,
            "handle": None,
            "url": None,
            "display_name": None,
            "posts_30d": None,
            "last_post_at": None,
            "posts_per_day": None,
            "duplicate_text_share": None,
            "default_avatar": None,
            "account_created_at": None,
            "owned_by_client": None,
            "country_signals": None,
            "lang_share": None,
            "keyword_ids": [],
            "route": route,
            "vendor": vendor,
            "review_flags": [],
            "provenance": prov(route, vendor, fields.pop("provenance_service", service), at),
            "retention_class": rclass,
        }
        msg.update(fields)
        return msg

    p = "docs/prds/"
    fbp = full(
        "fb-page-resolver",
        "01J9N6D1W5Q8Z2T7K4V0M3RXBH",
        "2026-10-06T10:41:09Z",
        "facebook:100064583471102",
        "facebook",
        "green",
        None,
        "meta_on_request",
        source_type="page",
        account_type="page",
        individual=False,
        public_account=True,
        platform_id="100064583471102",
        handle="exampletelecom.iq",
        url="https://www.facebook.com/exampletelecom.iq",
        display_name="شركة المثال للاتصالات",
        followers=412000,
        verified=True,
        owned_by_client=False,
        country_signals=signals(
            iraqi_place=True,
            iq_domain=True,
            evidence=[
                {"signal": "iraqi_place", "matched": "Baghdad", "where": "location.city"},
                {"signal": "iq_domain", "matched": "example-telecom.iq", "where": "website"},
            ],
        ),
        cached_until="2026-11-05T10:41:09Z",
        extras={
            "category": "Telecommunication Company",
            "location": {"city": "Baghdad", "country": "Iraq"},
            "website_domains": ["example-telecom.iq"],
            "about": "خدمة الإنترنت والاتصالات في بغداد والمحافظات",
        },
    )
    valid(s, "prd-fb-page-resolver", fbp)
    r_flatprofile = "the nested envelope and profile become ADR-0033's flat message; resolved_type gives way to account_type (ADR-0033)"
    r_cache = "cache becomes cached and cached_until (ADR-0033)"
    prd(
        "fb-page-resolver",
        p + "facebook/fb-page-resolver.md",
        101,
        s,
        "prd-fb-page-resolver",
        [
            R_META,
            R_PROV,
            r_flatprofile,
            r_cache,
            "is_verified becomes verified; signals become country_signals with signal_evidence (ADR-0033)",
            "category, location, website_domains and about move into extras, fb-page-resolver's declared keys",
            "a Page is an organisation kind, so public_account true (ADR-0010; Q7)",
        ],
    )
    igp = full(
        "ig-account-resolver",
        "01J9N8H3S5J7B9D2Z4W6Y8NPXK",
        "2026-10-06T12:40:11Z",
        "instagram:furat_restaurant",
        "instagram",
        "green",
        None,
        "meta_on_request",
        source_type="account",
        account_type="business_or_creator",
        individual=False,
        public_account=False,
        platform_id="17841400112233445",
        handle="furat_restaurant",
        url="https://www.instagram.com/furat_restaurant/",
        display_name="مطعم الفرات",
        followers=48200,
        owned_by_client=False,
        country_signals=signals(
            iraqi_place=True,
            phone_964=True,
            iq_domain=True,
            evidence=[
                {"signal": "iraqi_place", "matched": "البصرة", "where": "biography"},
                {"signal": "phone_964", "matched": "+964 770", "where": "biography"},
                {"signal": "iq_domain", "matched": "example.iq", "where": "website"},
            ],
        ),
        cached_until="2026-11-05T12:40:11Z",
        extras={
            "media_count": 913,
            "biography": "مطعم عراقي في البصرة. للحجز: +964 770 000 0000",
            "website": "https://example.iq",
        },
    )
    valid(s, "prd-ig-account-resolver", igp)
    prd(
        "ig-account-resolver",
        p + "instagram/ig-account-resolver.md",
        104,
        s,
        "prd-ig-account-resolver",
        [
            R_META,
            "resolution becomes status; account_class becomes account_type (ADR-0033)",
            r_cache,
            "job_id and attempt go: producer.job_id carries the resolve job (ADR-0002, ADR-0006)",
            "the old signal vocabulary (website_tld, city_in_bio) becomes country_signals' six booleans with signal_evidence (ADR-0033)",
            "media_count, biography and website move into extras",
            "business_or_creator is a person kind: public_account false on Instagram (ADR-0010 L72; Q7)",
        ],
    )
    lip = full(
        "li-org-resolver",
        "01M48AMMG0BSDJZYJZ2V3SKTWF",
        "2026-10-06T10:02:51Z",
        candidate_key_from_handle("linkedin", "example-bank"),
        "linkedin",
        "amber",
        "harvestapi",
        "linkedin_org",
        source_type="company_page",
        account_type="company_page",
        individual=False,
        public_account=True,
        platform_id="urn:li:organization:1234567",
        handle="example-bank",
        url="https://www.linkedin.com/company/example-bank/",
        display_name="Example Bank",
        followers=12400,
        owned_by_client=False,
        last_post_at="2026-10-04T08:15:00Z",
        posts_per_day=0.4,
        duplicate_text_share=0.05,
        country_signals=signals(
            iraqi_place=True,
            phone_964=True,
            iq_domain=True,
            evidence=[{"signal": "iraqi_place", "matched": "Baghdad", "where": "location"}],
        ),
        lang_share=share(ar=0.65, en=0.35, ar_iraqi=0.65, sample=20),
        extras={"posts_sampled": 20},
    )
    valid(s, "prd-li-org-resolver", lip)
    prd(
        "li-org-resolver",
        p + "linkedin/li-org-resolver.md",
        81,
        s,
        "prd-li-org-resolver",
        [
            R_META,
            R_PROV,
            "the key linkedin:org:<slug> becomes linkedin:<handle>, one of the four forms (ADR-0032)",
            "resolution becomes status (ADR-0033)",
            "country_signals and lang_share take ADR-0033's keys (ar_iq becomes ar_iraqi)",
            "posts_sampled moves into extras",
            "an organisation's profile takes linkedin_org (ADR-0055)",
        ],
    )
    site_id = "5e3b8f02-6d1c-4a97-b2e8-0c9f4d7a1e63"
    nsp = full(
        "news-site-resolver",
        "01M486K7W0KPR5FKH5ET9K2SFS",
        "2026-10-06T08:52:40Z",
        news_site_candidate_key("example-daily.iq"),
        "news",
        "green",
        None,
        "news_excerpt",
        source_type="site",
        account_type="site",
        individual=False,
        public_account=True,
        platform_id="example-daily.iq",
        handle="example-daily.iq",
        url="https://www.example-daily.iq/",
        display_name="Example Daily",
        owned_by_client=False,
        country_signals=signals(
            iraqi_place=True,
            phone_964=True,
            iq_domain=True,
            seed_list=True,
            evidence=[
                {"signal": "iq_domain", "matched": ".iq", "where": "host"},
                {"signal": "iraqi_place", "matched": "Baghdad", "where": "masthead"},
            ],
        ),
        lang_share=share(ar=0.95, en=0.05, ar_iraqi=0.05, sample=50),
        proposed_source_id=site_id,
        extras={
            "host": "www.example-daily.iq",
            "site_profile": {
                "feeds": [
                    {
                        "url": "https://www.example-daily.iq/feed",
                        "format": "rss2",
                        "items": 50,
                        "newest_at": "2026-10-06T05:41:00Z",
                        "has_body": False,
                    }
                ],
                "news_sitemap": "https://www.example-daily.iq/sitemap-news.xml",
                "sitemaps": ["https://www.example-daily.iq/sitemap_index.xml"],
                "homepage_diff": False,
                "article_url_patterns": [
                    "^https://www\\.example-daily\\.iq/[a-z-]+/[0-9]{4}/[0-9]{2}/[0-9]{2}/[^/?#]+$"
                ],
                "comments_provider": "disqus",
                "disqus_shortname": "exampledaily",
                "access_mode": "direct",
                "articles_per_day_estimate": 31,
                "last_article_at": "2026-10-06T05:41:00Z",
            },
            "proposed_tier": 1,
            "discovered_by": "search-hit-router",
            "crawl_allowed": True,
        },
    )
    valid(s, "prd-news-site-resolver", nsp)
    prd(
        "news-site-resolver",
        p + "news/news-site-resolver.md",
        81,
        s,
        "prd-news-site-resolver",
        [
            R_META,
            R_PROV,
            "kind: site goes; proposed_source flattens into the profile; the pre-allocated id travels as proposed_source_id (ADR-0033, ADR-0040)",
            "host, site_profile, proposed_tier, discovered_by and crawl_allowed move into extras",
            "times written in UTC with Z",
            "country_signals and lang_share take ADR-0033's keys",
            "a news domain is the organisation kind site, public_account true (ADR-0010; Q7)",
        ],
    )
    tgp = full(
        "tg-channel-resolver",
        "01M48A2Q70TMKPRYDBNVW331AB",
        "2026-10-06T03:40:12Z",
        candidate_key_from_handle("telegram", "basra_prices"),
        "telegram",
        "amber",
        "telemetrio",
        "vendor_agreed",
        source_type="channel",
        account_type="channel",
        individual=False,
        public_account=True,
        platform_id="basra_prices",
        handle="basra_prices",
        url="https://t.me/basra_prices",
        display_name="أسعار البصرة",
        followers=48210,
        owned_by_client=False,
        country_signals=signals(
            iraqi_place=True,
            platform_country_iq=True,
            evidence=[
                {"signal": "platform_country_iq", "matched": "IQ", "where": "vendor country"},
                {"signal": "iraqi_place", "matched": "البصرة", "where": "title"},
            ],
        ),
        lang_share=share(ar=0.95, ckb=0.05, ar_iraqi=0.71, sample=34),
        extras={"category": "news", "growth": {"subscribers_30d": 1930}},
    )
    valid(s, "prd-tg-channel-resolver", tgp)
    prd(
        "tg-channel-resolver",
        p + "telegram/tg-channel-resolver.md",
        81,
        s,
        "prd-tg-channel-resolver",
        [
            R_META,
            R_PROV,
            "idempotency_key goes; candidate_key added (ADR-0033)",
            "country_signals and lang_share take ADR-0033's keys (vendor_country becomes platform_country_iq; ar-iq becomes ar_iraqi)",
            "category and growth move into extras",
        ],
    )
    ttp = full(
        "tt-user-resolver",
        "01J9N6F1V8B3H5Q2Z7C4M0TXRA",
        "2026-10-06T10:02:31Z",
        "tiktok:6812345678901234567",
        "tiktok",
        "amber",
        "tikhub",
        "vendor_agreed",
        source_type="creator",
        account_type="creator",
        individual=False,
        public_account=False,
        platform_id="6812345678901234567",
        handle="basra.store",
        url="https://www.tiktok.com/@basra.store",
        display_name="متجر البصرة",
        followers=18400,
        verified=False,
        owned_by_client=False,
        country_signals=signals(
            iraqi_place=True,
            platform_country_iq=True,
            iq_domain=True,
            evidence=[{"signal": "platform_country_iq", "matched": "IQ", "where": "region"}],
        ),
        extras={
            "video_count": 212,
            "region": "IQ",
            "bio": "أفضل الأسعار في البصرة | 07701234567",
            "bio_link": "https://basra-store.iq",
        },
    )
    valid(s, "prd-tt-user-resolver", ttp)
    prd(
        "tt-user-resolver",
        p + "tiktok/tt-user-resolver.md",
        88,
        s,
        "prd-tt-user-resolver",
        [
            R_META,
            R_PROV,
            r_flatprofile,
            "idempotency_key and cache_hit go (ADR-0033)",
            "creator_threshold_met gives way to account_type creator (ADR-0033)",
            "a TikTok creator is a person kind, never listable: public_account false (ADR-0010 L70; Q7)",
            "video_count, region, bio and bio_link move into extras",
        ],
    )
    xp = full(
        "x-user-resolver",
        "01J9N8F4C2X7W1R5T3M6Q0ZKDA",
        "2026-10-06T11:02:37Z",
        "x:1456789012345678901",
        "x",
        "green",
        None,
        "x_24h_sync",
        source_type="account",
        account_type="organization_or_public_figure",
        individual=False,
        public_account=True,
        platform_id="1456789012345678901",
        handle="example_telecom_iq",
        url="https://x.com/example_telecom_iq",
        display_name="شركة المثال للاتصالات",
        followers=18400,
        verified=True,
        owned_by_client=False,
        account_created_at="2019-03-14T08:22:51Z",
        post_count=5310,
        cached_until="2026-11-05T11:02:37Z",
        country_signals=signals(
            iraqi_place=True,
            iq_domain=True,
            evidence=[
                {"signal": "iraqi_place", "matched": "Baghdad", "where": "location"},
                {"signal": "iq_domain", "matched": "example-telecom.iq", "where": "description"},
            ],
        ),
        extras={
            "following": 212,
            "location_text": "بغداد، العراق",
            "description": "الحساب الرسمي لشركة المثال | example-telecom.iq",
            "url_domain": "example-telecom.iq",
            "account_age_days": 2763,
        },
    )
    valid(s, "prd-x-user-resolver", xp)
    prd(
        "x-user-resolver",
        p + "x/x-user-resolver.md",
        103,
        s,
        "prd-x-user-resolver",
        [
            R_META,
            R_PROV,
            r_flatprofile,
            r_cache,
            "qualifies_as and qualifies_by give way to account_type and the verified flag (ADR-0033)",
            "post_count is the field x-full-archive-search reads (ADR-0033)",
            "following, location_text, description, url_domain and account_age_days move into extras",
            "a verified account passes the public test: public_account true (ADR-0010)",
        ],
    )
    ytp = full(
        "yt-channel-resolver",
        "01J9N7K3F2X6B8R1T5W9C4MZQD",
        "2026-10-06T11:02:47Z",
        "youtube:UC4fE2vQm8bN1kT7yR3pL9sA",
        "youtube",
        "green",
        None,
        "youtube_30d_text",
        source_type="channel",
        account_type="channel",
        individual=False,
        public_account=True,
        platform_id="UC4fE2vQm8bN1kT7yR3pL9sA",
        handle="@exampletv",
        url="https://www.youtube.com/channel/UC4fE2vQm8bN1kT7yR3pL9sA",
        display_name="قناة المثال الفضائية",
        followers=412000,
        owned_by_client=False,
        cached_until="2026-11-05T11:02:47Z",
        country_signals=signals(
            iraqi_place=True,
            platform_country_iq=True,
            iq_domain=True,
            evidence=[
                {"signal": "platform_country_iq", "matched": "IQ", "where": "snippet.country"}
            ],
        ),
        extras={
            "description": "أخبار العراق من بغداد والبصرة https://example-tv.iq/live",
            "country": "IQ",
            "country_source": "snippet",
            "default_language": "ar",
            "video_count": 3150,
            "view_count": 98000000,
            "published_at": "2014-03-09T08:15:22Z",
            "uploads_playlist_id": "UU4fE2vQm8bN1kT7yR3pL9sA",
            "website_domains": ["example-tv.iq"],
            "made_for_kids": None,
            "description_lang": "ar",
        },
    )
    valid(s, "prd-yt-channel-resolver", ytp)
    prd(
        "yt-channel-resolver",
        p + "youtube/yt-channel-resolver.md",
        105,
        s,
        "prd-yt-channel-resolver",
        [
            R_META,
            R_PROV,
            r_flatprofile,
            r_cache,
            "verdict becomes status; subscribers_hidden false needs no flag (ADR-0033)",
            "ids_in_call goes",
            "the channel's description, country, uploads playlist id and counts move into extras (ADR-0065 c))",
            "signals become country_signals",
        ],
    )
    prp = full(
        "poster-resolver",
        "01M48B9AKGRHAJW420WYJS5QK2",
        "2026-10-06T10:13:58Z",
        "instagram:17841400000000000",
        "instagram",
        "green",
        None,
        "meta_on_request",
        produced_at="2026-10-06T10:14:02Z",
        provenance_service="ig-account-resolver",
        source_type="account",
        account_type="business_or_creator",
        individual=False,
        public_account=False,
        platform_id="17841400000000000",
        handle="baghdad_eats",
        url="https://instagram.com/baghdad_eats",
        display_name="Baghdad Eats",
        verified=False,
        followers=48200,
        posts_30d=22,
        last_post_at="2026-10-05T19:40:00Z",
        owned_by_client=False,
        cached=True,
        cached_until="2026-11-05T10:13:58Z",
        keyword_ids=["0cd402b6-9015-45f8-86b4-d90cc086d320"],
        country_signals=signals(
            iraqi_place=True,
            evidence=[{"signal": "iraqi_place", "matched": "Baghdad", "where": "location"}],
        ),
        lang_share=share(ar=0.90, en=0.10, ar_iraqi=0.70, sample=22),
    )
    valid(s, "prd-poster-resolver", prp)
    prd(
        "poster-resolver",
        p + "shared/poster-resolver.md",
        91,
        s,
        "prd-poster-resolver",
        [
            "poster-resolver writes the topic only to re-emit a cached profile, cached: true (ADR-0032)",
            "schema_version becomes schema; service goes; producer stamped (ADR-0002)",
            "resolver becomes provenance.service, the resolver that fetched it (ADR-0003)",
            "keywords becomes keyword_ids; location_text goes (ADR-0033)",
            "hits_30d moves to poster_profiles.hits_30d (ADR-0045); unresolvable gives way to status (ADR-0033)",
            "lang_share takes ADR-0033's keys",
            "account_type business becomes business_or_creator, public_account false: ig-account-resolver writes business_or_creator (Q7; ig-account-resolver.md L60, L92; ADR-0010 L72)",
        ],
    )
    ind = {
        **meta(s, "x-user-resolver", "01J9N8F4C2X7W1R5T3M6Q0ZKDB", "2026-10-06T11:03:10Z"),
        "platform": "x",
        "status": "resolved",
        "reason": None,
        "followers": 48,
        "verified": False,
        "client_ids": [CLIENT],
        "resolved_at": "2026-10-06T11:03:10Z",
        "cached": False,
        "cached_until": "2026-11-05T11:03:10Z",
        "author_ref": ref("1000000000000000001", "x"),
        "account_type": "individual",
        "individual": True,
        "public_account": False,
        "provenance": prov("green", None, "x-user-resolver", "2026-10-06T11:03:10Z"),
        "retention_class": "x_24h_sync",
    }
    valid(s, "individual", ind)
    valid(
        s,
        "review-age-gated",
        {
            **igp,
            "status": "review",
            "reason": "age_gated",
            "account_type": None,
            "individual": None,
            "public_account": None,
        },
    )
    valid(
        s,
        "unresolvable-not-found",
        {
            **fbp,
            "status": "unresolvable",
            "reason": "not_found",
            "account_type": None,
            "individual": None,
            "public_account": None,
            "handle": None,
            "url": None,
            "display_name": None,
            "followers": None,
            "verified": None,
            "country_signals": None,
            "extras": {},
            "platform_id": "100064583471102",
        },
    )
    valid(
        s, "refresh-registered-source", {**xp, "source_id": "a4d2c9e1-5b7f-4e3a-8c60-2f1b9d7e4a35"}
    )
    valid(
        s,
        "public-person-individual",
        {
            **xp,
            **meta(s, "x-user-resolver", "01J9N8F4C2X7W1R5T3M6Q0ZKDC", "2026-10-06T11:04:00Z"),
            "candidate_key": "x:1000000000000000004",
            "platform_id": "1000000000000000004",
            "handle": "example_public_figure_x",
            "url": "https://x.com/example_public_figure_x",
            "display_name": "د. علي",
            "account_type": "individual",
            "individual": True,
            "public_account": True,
            "verified": True,
            "followers": 950,
            "extras": {},
        },
    )
    valid(s, "manual-origin", {**fbp, "origin": "manual"})
    metadata_invalids(s, fbp)
    for f, v in (
        ("handle", "example_poster_x"),
        ("display_name", "Abu Ali"),
        ("url", "https://x.com/example_poster_x"),
        ("country_signals", signals()),
        ("extras", {"following": 3}),
    ):
        invalid(
            s,
            f"individual-with-{f.replace('_', '-')}",
            with_(ind, (f,), v),
            [f],
            f"an ordinary individual's answer carries no {f} (ADR-0033, ADR-0010)",
        )
    invalid(
        s,
        "individual-full-set",
        {**xp, "account_type": "individual", "individual": True, "public_account": False},
        ["public_account"],
        "an ordinary individual's answer is the minimised one (ADR-0033)",
    )
    # A typed account is marked public or not: null goes with account_type null only.
    invalid(
        s,
        "individual-public-null",
        {
            **xp,
            "candidate_key": "x:1000000000000000002",
            "platform_id": "1000000000000000002",
            "handle": "example_person_x",
            "display_name": "Example Person",
            "url": "https://x.com/example_person_x",
            "account_type": "individual",
            "individual": True,
            "public_account": None,
            "verified": False,
            "followers": 48,
            "extras": {},
        },
        ["public_account"],
        "a typed account is marked public or not (ADR-0010 L59, ADR-0033 L26)",
    )
    invalid(
        s,
        "creator-public-null",
        {**xp, "account_type": "creator", "individual": False, "public_account": None},
        ["public_account"],
        "a typed account is marked public or not (ADR-0010 L59, ADR-0033 L26)",
    )
    invalid(
        s,
        "individual-flag-mismatch",
        {**xp, "account_type": "page", "individual": True},
        ["individual"],
        "individual is true exactly when account_type is individual (ADR-0033)",
    )
    invalid(
        s,
        "tiktok-person-public",
        {**ttp, "public_account": True},
        ["public_account"],
        "no TikTok person's account is listable (ADR-0010 L70)",
    )
    invalid(
        s,
        "organisation-not-public",
        {**fbp, "public_account": False},
        ["public_account"],
        "an organisation kind is a public account (ADR-0010)",
    )
    invalid(
        s,
        "resolved-with-reason",
        {**fbp, "reason": "not_found"},
        ["reason"],
        "a resolved answer carries no reason (ADR-0033)",
    )
    invalid(
        s,
        "review-without-reason",
        {**igp, "status": "review"},
        ["reason"],
        "a review answer names its reason (ADR-0033)",
    )
    invalid(
        s,
        "review-with-unresolvable-reason",
        {**igp, "status": "review", "reason": "suspended"},
        ["reason"],
        "the reason belongs to the status (Q8)",
    )
    invalid(
        s,
        "resolved-type",
        with_(fbp, ("resolved_type",), "page"),
        ["resolved_type"],
        "resolved_type gives way to account_type (ADR-0033)",
    )
    invalid(
        s,
        "extras-not-declared",
        with_(fbp, ("extras", "media_count"), 10),
        ["extras", "media_count"],
        "extras hold the resolver's declared keys only (ADR-0033)",
    )
    invalid(
        s,
        "cached-reemit-not-cached",
        {**prp, "cached": False},
        ["cached"],
        "poster-resolver writes only cached re-emits (ADR-0032)",
    )
    invalid(
        s,
        "key-platform-mismatch",
        {**fbp, "platform": "instagram"},
        ["candidate_key"],
        "the candidate key's platform is the profile's",
    )
    invalid(
        s,
        "old-lang-share",
        with_(lip, ("lang_share",), {"ar_iq": 0.65, "ckb": 0.0, "en": 0.35}),
        ["lang_share", "ar_iq"],
        "lang_share takes ADR-0033's keys",
    )
    invalid(
        s,
        "hits-30d",
        with_(fbp, ("hits_30d",), 3),
        ["hits_30d"],
        "hits_30d moves to poster_profiles (ADR-0045)",
    )
    tolerant(s, "unknown-field", with_(fbp, ("audience_estimate",), 12))
    tolerant(s, "unknown-extras-key", with_(fbp, ("extras", "page_category_id"), "2252"))


def analysis() -> None:
    s = "items.analysis/v1"

    def base(
        service: str,
        version: str,
        job: str,
        at: str,
        task: str,
        model: str,
        result: Any,
        **extra: Any,
    ) -> dict[str, Any]:
        msg = {
            **meta(s, service, job, at, version),
            "analysis_key": analysis_key(FB_ITEM, task, model),
            "input_hash": "sha256:" + content_hash(None, task + model)[7:],
            "item_id": FB_ITEM,
            "task": task,
            "model_version": model,
            "item_created_at": "2026-10-06T08:51:40Z",
            "item_version": 1,
            "content_hash": content_hash(None, FB_TEXT),
            "platform": "facebook",
            "kind": "post",
            "source_id": FB_SOURCE,
            "run_kind": "live",
            "lane": "priority",
            "status": "ok",
            "reason": None,
            "lang": "ar",
            "dialect": "iraqi",
            "expires_at": None,
            "result": result,
            "provenance": FB_PROV,
            "retention_class": "meta_on_request",
        }
        msg.update(extra)
        return msg

    r_an = [
        R_PROV,
        "item_fetched_at goes: provenance.fetched_at carries it (ADR-0003)",
        "item_created_at added (ADR-0023)",
        "item_id is normalize-item's item, derived from its key; content_hash and input_hash in full (ADR-0006, ADR-0009)",
    ]
    ent = base(
        "analysis-entities",
        "0.2.0",
        "01M4886GG00N55MK92G5KMGQ7G",
        "2026-10-06T09:15:14Z",
        "entities",
        "ent-iq-2026.11",
        {
            "entities": [
                {
                    "type": "place",
                    "entity_id": "kb-pl-0007",
                    "name_en": "Basra",
                    "level": "city",
                    "governorate_id": "kb-pl-0003",
                    "surface": "بالبصرة",
                    "start": 12,
                    "end": 19,
                    "link_score": 0.96,
                    "source": "both",
                }
            ],
            "unlinked": [],
            "private_person_mentions": 0,
        },
        kb_version=14,
    )
    valid(s, "prd-analysis-entities", ent)
    prd(
        "analysis-entities",
        "docs/prds/shared/analysis-entities.md",
        92,
        s,
        "prd-analysis-entities",
        r_an,
    )
    ocr = base(
        "analysis-media",
        "0.2.0",
        "01M4886GG0GDQ0Y9RD0QSBJD30",
        "2026-10-06T09:16:02Z",
        "media_ocr",
        "ocr-iq-2026.11",
        {
            "media": [
                {
                    "index": 0,
                    "type": "image",
                    "sha256": "d41f" + "0" * 56 + "a9c2",
                    "reused": False,
                    "text": "لا يوجد اتصال بالانترنت",
                    "lang": "ar",
                    "script": "arab",
                    "confidence": 0.88,
                    "frames": None,
                    "truncated": False,
                }
            ]
        },
        lang=None,
        dialect=None,
    )
    valid(s, "prd-analysis-media", ocr)
    prd(
        "analysis-media",
        "docs/prds/shared/analysis-media.md",
        89,
        s,
        "prd-analysis-media",
        [*r_an, "the media hash written in full"],
    )
    sent = base(
        "analysis-sentiment",
        "0.3.0",
        "01M4886GG018V1FH131HTSP75D",
        "2026-10-06T09:15:12Z",
        "sentiment",
        "sent-iq-2026.11",
        {
            "label": "negative",
            "score": -0.63,
            "confidence": 0.68,
            "probs": {"positive": 0.05, "negative": 0.68, "neutral": 0.21, "mixed": 0.06},
            "low_confidence": False,
            "sarcasm_prob": 0.04,
            "sarcasm_flag": False,
            "code_switched": False,
            "truncated": False,
            "model_route": "ar",
        },
        preproc_version="pp-2026.10",
    )
    valid(s, "prd-analysis-sentiment", sent)
    prd(
        "analysis-sentiment",
        "docs/prds/shared/analysis-sentiment.md",
        91,
        s,
        "prd-analysis-sentiment",
        r_an,
    )
    top = base(
        "analysis-topics",
        "0.2.0",
        "01M4886GG040V4RTSSHFBF6ADK",
        "2026-10-06T09:15:15Z",
        "topics.global",
        "topics-iq-2026.11.tx7",
        {
            "topics": [
                {"topic_id": "global:outage", "score": 0.93, "source": "supervised"},
                {"topic_id": "global:customer_support", "score": 0.41, "source": "supervised"},
            ],
            "top_topic": "global:outage",
            "intent": {"label": "question", "score": 0.72},
            "low_confidence": False,
        },
        taxonomy_version=7,
    )
    valid(s, "prd-analysis-topics", top)
    prd(
        "analysis-topics",
        "docs/prds/shared/analysis-topics.md",
        95,
        s,
        "prd-analysis-topics",
        [
            *r_an,
            "the task topics:global becomes topics.global, task names hold no colon (ADR-0023)",
            "node_id becomes topic_id = <taxonomy_id>:<node_id> (ADR-0023, ADR-0048)",
        ],
    )
    aspect = valid(
        s,
        "sentiment-aspect",
        base(
            "analysis-sentiment",
            "0.3.0",
            "01M4886GG018V1FH131HTSP75E",
            "2026-10-06T09:15:13Z",
            "sentiment_aspect",
            "sent-iq-2026.11",
            {
                "targets": [
                    {
                        "keyword_id": "9a8b7c6d-5e4f-4321-a0b9-c8d7e6f5a4b3",
                        "label": "negative",
                        "score": -0.7,
                        "matched_term": "النت",
                        "offsets": [[0, 3]],
                        "confidence": 0.71,
                    }
                ]
            },
        ),
    )
    cluster = valid(
        s,
        "topic-cluster",
        base(
            "analysis-topics",
            "0.2.0",
            "01M4886GG040V4RTSSHFBF6ADM",
            "2026-10-06T09:15:16Z",
            "topic_cluster",
            "clu-2026.11",
            {"cluster_id": "c-20261006-0042"},
        ),
    )
    fetch = valid(
        s,
        "media-fetch",
        base(
            "analysis-media",
            "0.2.0",
            "01M4886GG0GDQ0Y9RD0QSBJD31",
            "2026-10-06T09:16:00Z",
            "media_fetch",
            "fetch-1",
            {
                "media": [
                    {
                        "index": 0,
                        "type": "image",
                        "sha256": "d41f" + "0" * 56 + "a9c2",
                        "reused": False,
                    }
                ]
            },
            lang=None,
            dialect=None,
        ),
    )
    tags = valid(
        s,
        "media-tags",
        base(
            "analysis-media",
            "0.2.0",
            "01M4886GG0GDQ0Y9RD0QSBJD32",
            "2026-10-06T09:16:03Z",
            "media_tags",
            "tags-2026.11",
            {
                "media": [
                    {
                        "index": 0,
                        "type": "image",
                        "sha256": "d41f" + "0" * 56 + "a9c2",
                        "reused": True,
                        "tags": [{"tag": "router", "score": 0.81}],
                    }
                ]
            },
            lang=None,
            dialect=None,
        ),
    )
    asr = valid(
        s,
        "media-asr",
        base(
            "analysis-media",
            "0.2.0",
            "01M4886GG0GDQ0Y9RD0QSBJD33",
            "2026-10-06T09:16:04Z",
            "media_asr",
            "asr-iq-2026.11",
            {
                "media": [
                    {
                        "index": 0,
                        "type": "video",
                        "sha256": "e52f" + "1" * 56 + "b0d3",
                        "reused": False,
                        "segments": [
                            {"start": 0.0, "end": 3.2, "text": "النت مقطوع", "confidence": 0.8}
                        ],
                        "lang": "ar",
                        "dialect": "iraqi",
                    }
                ]
            },
        ),
    )
    logo = valid(
        s,
        "media-logo",
        base(
            "analysis-media",
            "0.2.0",
            "01M4886GG0GDQ0Y9RD0QSBJD34",
            "2026-10-06T09:16:05Z",
            "media_logo",
            "logo-2026.11",
            {
                "media": [
                    {
                        "index": 0,
                        "type": "image",
                        "sha256": "d41f" + "0" * 56 + "a9c2",
                        "reused": True,
                        "logos": [
                            {
                                "brand_id": "brand-0042",
                                "score": 0.77,
                                "box": [10, 20, 110, 80],
                                "frame_time": None,
                            }
                        ],
                    }
                ]
            },
            lang=None,
            dialect=None,
        ),
    )
    skipped = base(
        "analysis-sentiment",
        "0.3.0",
        "01M4886GG018V1FH131HTSP75F",
        "2026-10-06T09:15:20Z",
        "sentiment",
        "sent-iq-2026.11",
        None,
        status="skipped",
        reason="no_text",
        lang=None,
        dialect=None,
    )
    valid(s, "skipped-no-text", skipped)
    valid(s, "skipped-ai-input-refused", {**skipped, "reason": "ai_input_refused"})
    valid(s, "rerun-standard-lane", {**sent, "run_kind": "rerun", "lane": "standard"})
    metadata_invalids(s, sent)
    invalid(
        s,
        "colon-task",
        {**top, "task": "topics:global"},
        ["task"],
        "task names hold no colon (ADR-0023)",
    )
    invalid(
        s,
        "analysis-key-not-the-helpers",
        {**sent, "analysis_key": analysis_key(FB_ITEM, "sentiment", "sent-iq-2026.10")},
        ["analysis_key"],
        "analysis_key = item_id:task:model_version (ADR-0023)",
    )
    invalid(
        s,
        "ok-without-result",
        {**sent, "result": None},
        ["result"],
        "an ok analysis carries its result",
    )
    invalid(
        s,
        "skipped-without-reason",
        {**skipped, "reason": None},
        ["reason"],
        "a skipped analysis names its reason (Q8)",
    )
    invalid(
        s,
        "skipped-with-result",
        {**skipped, "result": sent["result"]},
        ["result"],
        "a skipped analysis carries no result",
    )
    invalid(
        s,
        "ok-with-reason",
        {**sent, "reason": "no_text"},
        ["reason"],
        "an ok analysis carries no reason",
    )
    invalid(
        s,
        "node-id",
        with_(top, ("result", "topics", 0, "node_id"), "outage"),
        ["result", "topics", 0, "node_id"],
        "topic ids are one field, topic_id (ADR-0023)",
    )
    invalid(
        s,
        "item-fetched-at",
        with_(sent, ("item_fetched_at",), "2026-10-06T09:13:58Z"),
        ["item_fetched_at"],
        "item_fetched_at gives way to provenance (ADR-0003)",
    )
    invalid(
        s,
        "sentiment-label",
        with_(sent, ("result", "label"), "angry"),
        ["result", "label"],
        "the sentiment labels are closed",
    )
    invalid(
        s,
        "unknown-skip-reason",
        {**skipped, "reason": "too_short"},
        ["reason"],
        "the skip reasons are closed (Q8)",
    )
    target = aspect["result"]["targets"][0]
    invalid(
        s,
        "aspect-matched-text",
        with_(
            aspect,
            ("result", "targets", 0),
            {
                **{k: v for k, v in target.items() if k != "matched_term"},
                "matched_text": target["matched_term"],
            },
        ),
        ["result", "targets", 0, "matched_text"],
        "matched_text takes ADR-0031's form, matched_term (ADR-0070)",
    )
    invalid(
        s,
        "cluster-without-id",
        with_(cluster, ("result",), {}),
        ["result", "cluster_id"],
        "a cluster result names its cluster",
    )
    invalid(
        s,
        "entities-private-person",
        with_(ent, ("result", "entities", 0, "type"), "person_private"),
        ["result", "entities", 0, "type"],
        "only public persons are linked entities; private ones are counted (analysis-entities §5.3)",
    )
    # The person guard: a person mention is linked or dropped, and an unlinked form is never a
    # person's (analysis-entities §5.3 L69, L71).
    invalid(
        s,
        "entities-person-without-id",
        with_(
            ent,
            ("result", "entities"),
            [
                *ent["result"]["entities"],
                {
                    "type": "person_public",
                    "entity_id": None,
                    "start": 0,
                    "end": 9,
                    "source": "model",
                    "surface": "د. المثال",
                },
            ],
        ),
        ["result", "entities", 1, "entity_id"],
        "a person mention is linked or dropped, never kept unlinked (analysis-entities §5.3 L69)",
    )
    invalid(
        s,
        "unlinked-person",
        with_(
            ent,
            ("result", "unlinked"),
            [{"type": "person_public", "surface": "د. المثال", "start": 0, "end": 9}],
        ),
        ["result", "unlinked", 0, "type"],
        "an unlinked form is never a person's (analysis-entities §5.3 L71)",
    )
    invalid(
        s,
        "media-fetch-short-hash",
        with_(fetch, ("result", "media", 0, "sha256"), "d41f"),
        ["result", "media", 0, "sha256"],
        "a media hash is 64 hex",
    )
    invalid(
        s,
        "ocr-confidence-above-one",
        with_(ocr, ("result", "media", 0, "confidence"), 1.2),
        ["result", "media", 0, "confidence"],
        "confidence is a share",
    )
    invalid(
        s,
        "tag-without-score",
        without(tags, "result", "media", 0, "tags", 0, "score"),
        ["result", "media", 0, "tags", 0, "score"],
        "a tag carries its score",
    )
    invalid(
        s,
        "asr-segment-without-end",
        without(asr, "result", "media", 0, "segments", 0, "end"),
        ["result", "media", 0, "segments", 0, "end"],
        "a speech segment names its end",
    )
    invalid(
        s,
        "logo-box-three-numbers",
        with_(logo, ("result", "media", 0, "logos", 0, "box"), [10, 20, 110]),
        ["result", "media", 0, "logos", 0, "box"],
        "a logo box is four numbers",
    )
    tolerant(s, "unknown-result-field", with_(sent, ("result", "emotion"), "frustration"))


def metrics_topic() -> None:
    s = "item.metrics/v1"
    fb_post = "100064583471102_1198837625012734"
    fb: dict[str, Any] = {
        **meta(s, "fb-reactions-fetcher", "01J9Q1M4V8N2B6X0C3Z7A5S9DF", "2026-10-07T07:14:53Z"),
        "item_id": iid("facebook", "post", fb_post),
        "idempotency_key": key("facebook", "post", fb_post),
        "platform": "facebook",
        "platform_id": fb_post,
        "source_id": "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11",
        "created_at": "2026-10-06T07:12:09Z",
        "observation": {"label": "refresh", "step": "+24h", "observed_at": "2026-10-07T07:14:51Z"},
        "metrics": {
            "views": None,
            "likes": 2421,
            "comments": 403,
            "shares": 58,
            "reactions_by_type": {
                "like": 2210,
                "love": 131,
                "haha": 19,
                "wow": 4,
                "sad": 1,
                "angry": 44,
                "care": 12,
            },
        },
        "provenance": prov("green", None, "fb-reactions-fetcher", "2026-10-07T07:14:51Z"),
        "retention_class": "meta_on_request",
    }
    valid(s, "prd-fb-reactions-fetcher", fb)
    r_obs = "the label refresh_24h becomes label refresh with step +24h (ADR-0034)"
    prd(
        "fb-reactions-fetcher",
        "docs/prds/facebook/fb-reactions-fetcher.md",
        104,
        s,
        "prd-fb-reactions-fetcher",
        [
            R_META,
            R_PROV,
            r_obs,
            "item_idempotency_key becomes idempotency_key; item_id added (ADR-0034)",
            "post_created_time becomes created_at; age_seconds goes, readers derive it (ADR-0034)",
            "reactions_total becomes likes, Facebook's total of all reactions; the types move into reactions_by_type (F-34)",
        ],
    )
    yt_vid = "Xy12AbCdEfG"
    yt: dict[str, Any] = {
        **meta(s, "yt-video-details-fetcher", "01JAD6P2R8S4T0V5W7X9Y3Z1AB", "2026-10-07T07:21:42Z"),
        "item_id": iid("youtube", "video", yt_vid),
        "idempotency_key": key("youtube", "video", yt_vid),
        "platform": "youtube",
        "platform_id": yt_vid,
        "source_id": "2b7d4e90-1c3a-4f6e-8d25-7a9b0c1e3f42",
        "created_at": "2026-10-06T07:12:09Z",
        "observation": {"label": "refresh", "step": "+24h", "observed_at": "2026-10-07T07:21:40Z"},
        "metrics": {
            "views": 48213,
            "likes": 1904,
            "comments": 377,
            "shares": None,
            "reactions_by_type": None,
        },
        "channel_id": "UCq3Ov8nVbT0xY1zKp2LmA4w",
        "live_state": "none",
        "provenance": prov("green", None, "yt-video-details-fetcher", "2026-10-07T07:21:40Z"),
        "retention_class": "youtube_30d_text",
    }
    valid(s, "prd-yt-video-details-fetcher", yt)
    prd(
        "yt-video-details-fetcher",
        "docs/prds/youtube/yt-video-details-fetcher.md",
        133,
        s,
        "prd-yt-video-details-fetcher",
        [
            R_META,
            R_PROV,
            r_obs,
            "item_idempotency_key becomes idempotency_key; item_id added",
            "post_created_time becomes created_at; age_seconds and call_id go (ADR-0034)",
            "kind post becomes video in the key (ADR-0007)",
        ],
        note="its raw.items example is under raw.items/v1",
    )
    tt_vid = "7421538806219533573"
    tt = {
        **meta(s, "tt-video-stats-refresher", "01J9N5D6T3K8R2W7Y0A4F1HXQB", "2026-10-07T09:31:17Z"),
        "item_id": iid("tiktok", "video", tt_vid),
        "idempotency_key": key("tiktok", "video", tt_vid),
        "platform": "tiktok",
        "platform_id": tt_vid,
        "source_id": "3d8a51c2-7e04-4b9f-8c16-2a9e5d70f4b8",
        "created_at": "2026-10-06T09:10:00Z",
        "observation": {"label": "refresh", "step": "+24h", "observed_at": "2026-10-07T09:31:15Z"},
        "metrics": {
            "views": 61250,
            "likes": 4410,
            "comments": 498,
            "shares": 312,
            "reactions_by_type": None,
        },
        "regressed": False,
        "provenance": prov("amber", "tikhub", "tt-video-stats-refresher", "2026-10-07T09:31:15Z"),
        "retention_class": "vendor_agreed",
    }
    valid(s, "prd-tt-video-stats-refresher", tt)
    prd(
        "tt-video-stats-refresher",
        "docs/prds/tiktok/tt-video-stats-refresher.md",
        87,
        s,
        "prd-tt-video-stats-refresher",
        [
            R_META,
            R_PROV,
            "the envelope and observation flatten into ADR-0034's message; the metrics:<key>:plus_24h key goes, item_key becomes idempotency_key",
            "the label plus_24h becomes refresh with step +24h (ADR-0034)",
            "first_seen_at, due_at, lateness_seconds, baseline_missing and client_ids go (ADR-0034)",
            "created_at is the video's creation time",
        ],
    )
    valid(
        s,
        "first-sight",
        {
            **fb,
            **meta(
                s,
                "normalize-item",
                "01J9N2Q7Z4T8X1V6M3K0H5R2WB",
                "2026-10-06T09:14:04Z",
                "1.4.0",
                "metrics",
            ),
            "observation": {
                "label": "first_sight",
                "step": None,
                "observed_at": "2026-10-06T09:13:58Z",
            },
            "provenance": prov("green", None, "fb-page-feed-poller", "2026-10-06T09:13:58Z"),
        },
    )
    valid(
        s,
        "refresh-client-request",
        with_(
            fb,
            ("observation",),
            {
                "label": "refresh",
                "step": "refresh:01J9R5S3V7W1X4Y8Z0A2B6C9DE",
                "observed_at": "2026-10-07T07:14:51Z",
            },
        ),
    )
    for label in ("poll", "backfill", "ops_force", "live_end"):
        valid(
            s,
            f"label-{label.replace('_', '-')}",
            with_(
                yt,
                ("observation",),
                {"label": label, "step": None, "observed_at": "2026-10-07T07:21:40Z"},
            ),
        )
    valid(s, "saves", with_(fb, ("metrics", "saves"), 31))
    metadata_invalids(s, fb)
    invalid(
        s,
        "refresh-without-step",
        with_(fb, ("observation", "step"), None),
        ["observation", "step"],
        "a refresh observation names its step (ADR-0034)",
    )
    invalid(
        s,
        "poll-with-step",
        with_(
            yt,
            ("observation",),
            {"label": "poll", "step": "+24h", "observed_at": "2026-10-07T07:21:40Z"},
        ),
        ["observation", "step"],
        "only refresh carries a step",
    )
    invalid(
        s,
        "old-label",
        with_(fb, ("observation", "label"), "refresh_24h"),
        ["observation", "label"],
        "refresh_24h gives way to refresh with step +24h (ADR-0034)",
    )
    invalid(
        s,
        "item-idempotency-key",
        with_(fb, ("item_idempotency_key",), fb["idempotency_key"]),
        ["item_idempotency_key"],
        "one name, idempotency_key (ADR-0034)",
    )
    invalid(
        s,
        "uppercase-reaction",
        with_(fb, ("metrics", "reactions_by_type"), {"LIKE": 2210}),
        ["metrics", "reactions_by_type", "LIKE"],
        "reaction types in lower case (F-34)",
    )
    invalid(
        s,
        "reactions-total",
        with_(fb, ("metrics", "reactions_total"), 2421),
        ["metrics", "reactions_total"],
        "Facebook's total is likes (F-34)",
    )
    invalid(
        s,
        "missing-metric",
        without(fb, "metrics", "shares"),
        ["metrics", "shares"],
        "each metric present, null where the platform has none (ADR-0034)",
    )
    invalid(
        s,
        "item-id-not-the-keys",
        with_(fb, ("item_id",), "3287bad6-f64e-566f-a071-6fdd4aca57dd"),
        ["item_id"],
        "item_id = uuid_v5(ns_items, key) (ADR-0006)",
    )
    invalid(
        s,
        "platform-not-the-keys",
        with_(fb, ("platform_id",), "100064583471102_1"),
        ["platform_id"],
        "the platform id is the key's",
    )
    invalid(
        s,
        "age-seconds",
        with_(fb, ("age_seconds",), 86562),
        ["age_seconds"],
        "readers derive age_seconds (ADR-0034)",
    )
    invalid(
        s,
        "not-a-metrics-writer",
        with_(fb, ("producer", "service"), "fb-page-feed-poller"),
        ["producer", "service"],
        "normalize-item and the count-only readers write item.metrics (ADR-0034)",
    )
    tolerant(s, "unknown-field", with_(fb, ("sample_rate",), 1))


def deletions() -> None:
    s = "deletions/v1"

    def dele(
        service: str,
        job: str,
        at: str,
        reason: str,
        scope: str,
        mode: str,
        key_field: str,
        key_value: str,
        target: dict[str, Any],
        signal_at: str,
        due_at: str,
        provenance: dict[str, Any],
        **extra: Any,
    ) -> dict[str, Any]:
        d = {
            **meta(s, service, job, at),
            "deletion_id": deletion_id(reason, scope, key_value, mode, signal_at, target),
            "reason": reason,
            "scope": scope,
            "mode": mode,
            key_field: key_value,
            "target": target,
            "signal_at": signal_at,
            "due_at": due_at,
            "provenance": provenance,
        }
        d.update(extra)
        return d

    tt_vid = "7421538806219533573"
    rp = dele(
        "retention-purger",
        "01J9P8A3V5N7B2D4F6H0K1M9QS",
        "2026-10-06T00:05:12Z",
        "retention",
        "item",
        "purge_text",
        "source_id",
        "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11",
        {
            "platform": "tiktok",
            "kind": "video",
            "item_ids": [iid("tiktok", "video", tt_vid)],
            "platform_ids": [tt_vid],
        },
        "2026-10-06T00:00:00Z",
        "2026-10-06T06:00:00Z",
        prov("amber", "tikhub", "tt-profile-videos-poller", "2026-07-07T23:40:00Z"),
        retention_class="vendor_agreed",
        requested_by="retention-purger",
        run_id="01J9P8A3V5N7B2D4F6H0K1M9QS",
    )
    valid(s, "prd-retention-purger", rp)
    r_del = [
        R_META,
        "deletion_id from the helper: del:<reason>:<scope>:<sha256 of {key, mode, signal_day, target}> (Q2; ADR-0035)",
        "client_id: null and emitted_at go: the client scope names its key, produced_at says when (ADR-0035)",
        "item_ids from the key helper, uuid v5 (ADR-0006)",
        "an item-scope deletion carries its items' provenance (ADR-0003 L28)",
    ]
    prd(
        "retention-purger",
        "docs/prds/shared/retention-purger.md",
        96,
        s,
        "prd-retention-purger",
        [
            *r_del,
            "the TikTok kind post becomes video (ADR-0007, ADR-0008)",
            "platform_ids added beside item_ids",
        ],
    )
    xid = "1842957310264891392"
    xc = dele(
        "x-compliance-sync",
        "01J9PB2C4E6G8J0K2M4P6R8T0V",
        "2026-10-06T02:51:09Z",
        "platform_sync",
        "item",
        "delete",
        "source_id",
        "3a7d9c21-5e4b-4f8a-b6c0-2d1e9f7a3b54",
        {
            "platform": "x",
            "kind": "post",
            "item_ids": [iid("x", "post", xid)],
            "platform_ids": [xid],
        },
        "2026-10-06T02:47:31Z",
        "2026-10-07T02:47:31Z",
        prov("green", None, "x-user-timeline-poller", "2026-10-05T19:40:00Z"),
        retention_class="x_24h_sync",
        requested_by="x-compliance-sync",
        run_id="01J9PB2C4E6G8J0K2M4P6R8T0V",
        event_at="2026-10-05T19:42:07Z",
    )
    valid(s, "prd-x-compliance-sync", xc)
    prd(
        "x-compliance-sync",
        "docs/prds/x/x-compliance-sync.md",
        99,
        s,
        "prd-x-compliance-sync",
        [*r_del, "platform_status, countries: null and x_job_id go (ADR-0035)"],
    )
    c1, c2 = "UgzK7pQ2mV9xR4tL1bN6AaABAg", "UgzK7pQ2mV9xR4tL1bN6AaABAg.9TqNw5Hc3Kp"
    yt = dele(
        "yt-text-purger",
        "01M47F0V80FZGG928KMD5XX36J",
        "2026-10-06T02:07:31Z",
        "retention",
        "item",
        "purge_text",
        "source_id",
        "2d7e9b41-5c3a-4f8e-b1d6-7a0c9e3f5b28",
        {
            "platform": "youtube",
            "kind": "comment",
            "item_ids": [iid("youtube", "comment", c1), iid("youtube", "comment", c2)],
            "platform_ids": [c1, c2],
            "fetched_before": "2026-10-06T02:00:00Z",
        },
        "2026-10-06T02:00:00Z",
        "2026-10-06T19:42:10Z",
        prov("green", None, "yt-comments-fetcher", "2026-09-05T23:58:12Z"),
        retention_class="youtube_30d_text",
        requested_by="yt-text-purger",
        run_id="01M47F0V80FZGG928KMD5XX36J",
    )
    valid(s, "prd-yt-text-purger", yt)
    prd(
        "yt-text-purger",
        "docs/prds/youtube/yt-text-purger.md",
        142,
        s,
        "prd-yt-text-purger",
        [
            *r_del,
            "scope text_only becomes item with mode purge_text (ADR-0035)",
            "video_id and parent_run_id go: the item ids name the comments (ADR-0035)",
        ],
    )
    author = dele(
        "retention-purger",
        "01J9Q8A3V5N7B2D4F6H0K1M9QA",
        "2026-10-06T10:00:05Z",
        "author_request",
        "author",
        "delete",
        "author_ref",
        ref("1000000000000000001", "x"),
        {"platform": "x"},
        "2026-10-06T09:58:00Z",
        "2026-11-05T09:58:00Z",
        prov(None, None, "retention-purger", "2026-10-06T09:58:00Z"),
        requested_by="retention-purger",
    )
    valid(s, "author-request", author)
    xa = dele(
        "x-compliance-sync",
        "01J9PB2C4E6G8J0K2M4P6R8T0W",
        "2026-10-06T02:52:00Z",
        "platform_sync",
        "author",
        "delete",
        "author_ref",
        ref("1290000000000000077", "x"),
        {"platform": "x", "user_ids": ["1290000000000000077"]},
        "2026-10-06T02:39:05Z",
        "2026-10-07T02:39:05Z",
        prov("green", None, "x-compliance-sync", "2026-10-06T02:39:05Z"),
        requested_by="x-compliance-sync",
        run_id="01J9PB2C4E6G8J0K2M4P6R8T0V",
    )
    valid(s, "author-x-compliance", xa)
    src = dele(
        "tt-client-videos-fetcher",
        "01J9N7H4S2P9D6K1X8V3B5WEMD",
        "2026-10-07T09:00:05Z",
        "authorization_revoked",
        "source",
        "delete",
        "source_id",
        "9a47e0b1-5c3d-4f82-b6e9-1d0c8a3f7e25",
        {"platform": "tiktok"},
        "2026-10-07T08:59:00Z",
        "2026-10-08T08:59:00Z",
        prov("green", None, "tt-client-videos-fetcher", "2026-10-07T08:59:00Z"),
    )
    valid(s, "source-authorization-revoked", src)
    cli = dele(
        "retention-purger",
        "01J9Q8A3V5N7B2D4F6H0K1M9QB",
        "2026-10-06T00:10:00Z",
        "client_offboarding",
        "client",
        "delete",
        "client_id",
        CLIENT2,
        {},
        "2026-10-06T00:00:00Z",
        "2026-10-13T00:00:00Z",
        prov(None, None, "retention-purger", "2026-10-06T00:00:00Z"),
        requested_by="retention-purger",
        run_id="01J9Q8A3V5N7B2D4F6H0K1M9QB",
    )
    valid(s, "client-offboarding", cli)
    creq = dele(
        "admin-api",
        "01J9R5S3V7W1X4Y8Z0A2B6C9DF",
        "2026-10-06T12:00:01Z",
        "client_request",
        "client",
        "purge_derived",
        "client_id",
        CLIENT,
        {"platform": "facebook", "item_ids": [FB_ITEM]},
        "2026-10-06T12:00:00Z",
        "2026-10-07T12:00:00Z",
        prov(None, None, "admin-api", "2026-10-06T12:00:00Z"),
        requested_by="person:01J9P2R4T6V8X0Z2B4D6F8H0KM",
    )
    valid(s, "client-request", creq)
    wh = dele(
        "x-compliance-sync",
        "01J9PB2C4E6G8J0K2M4P6R8T0X",
        "2026-10-06T02:53:00Z",
        "legal",
        "item",
        "withhold",
        "source_id",
        "3a7d9c21-5e4b-4f8a-b6c0-2d1e9f7a3b54",
        {
            "platform": "x",
            "kind": "post",
            "item_ids": [iid("x", "post", "1842957310264891999")],
            "platform_ids": ["1842957310264891999"],
            "countries": ["IQ"],
        },
        "2026-10-06T02:47:31Z",
        "2026-10-07T02:47:31Z",
        prov("green", None, "x-user-timeline-poller", "2026-10-05T19:41:00Z"),
        retention_class="x_24h_sync",
        requested_by="x-compliance-sync",
    )
    valid(s, "item-withhold", wh)
    multi_ids = sorted(
        [("100064583471102_1198837625012734", "post"), ("100064583471102_1176002458962861", "post")]
    )
    multi = dele(
        "retention-purger",
        "01J9Q8A3V5N7B2D4F6H0K1M9QC",
        "2026-10-06T00:06:00Z",
        "retention",
        "item",
        "delete",
        "source_id",
        "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11",
        {
            "platform": "facebook",
            "kind": "post",
            "item_ids": sorted(iid("facebook", k, p) for p, k in multi_ids),
            "platform_ids": [p for p, _ in multi_ids],
        },
        "2026-10-06T00:00:00Z",
        "2026-10-06T06:00:00Z",
        prov("green", None, "fb-page-feed-poller", "2026-10-06T09:15:42Z"),
        retention_class="meta_on_request",
        requested_by="retention-purger",
        run_id="01J9Q8A3V5N7B2D4F6H0K1M9QC",
    )
    valid(s, "item-multi", multi)
    metadata_invalids(s, xc)
    invalid(
        s,
        "class-on-author-scope",
        {**author, "retention_class": "x_24h_sync"},
        ["retention_class"],
        "a non-item deletion carries no retention_class (ADR-0003 L28)",
    )
    invalid(
        s,
        "unknown-requester",
        {**author, "requested_by": "no-such-service"},
        ["requested_by"],
        "a requester that names a service is one the registry lists (Q18; F-09)",
    )
    invalid(
        s,
        "route-on-author-request",
        with_(author, ("provenance", "route"), "green"),
        ["provenance", "route"],
        "a signal that is no fetch has a null route (F-08)",
    )
    invalid(
        s,
        "null-route-on-platform-sync",
        with_(src, ("provenance", "route"), None),
        ["provenance", "route"],
        "a fetch signal names its route (F-08)",
    )
    invalid(
        s,
        "vendor-without-route",
        with_(author, ("provenance", "vendor"), "sociavault"),
        ["provenance", "vendor"],
        "no vendor without a route",
    )
    invalid(
        s,
        "deletion-id-not-the-helpers",
        {
            **xc,
            "deletion_id": "del:platform_sync:item:9d2e4b7a1c0f3e58b6a9d4c2e7f1b3a5d8c0e6f2a4b9d1c3e5f7a0b2c4d6e8f1",
        },
        ["deletion_id"],
        "deletion_id from the helper (Q2)",
    )
    invalid(
        s,
        "client-scope-with-source",
        {**cli, "source_id": "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11"},
        ["source_id"],
        "a client-scope deletion names client_id only (R-1)",
    )
    invalid(
        s,
        "text-only-scope",
        {**yt, "scope": "text_only"},
        ["scope"],
        "text_only becomes item with purge_text (ADR-0035)",
    )
    invalid(
        s,
        "detected-at",
        {**xc, "detected_at": "2026-10-06T02:47:31Z"},
        ["detected_at"],
        "detected_at becomes signal_at (ADR-0035)",
    )
    invalid(
        s,
        "admin-platform-sync",
        {
            **creq,
            "reason": "platform_sync",
            "deletion_id": deletion_id(
                "platform_sync",
                "client",
                CLIENT,
                "purge_derived",
                "2026-10-06T12:00:00Z",
                creq["target"],
            ),
            "provenance": prov("green", None, "admin-api", "2026-10-06T12:00:00Z"),
        },
        ["reason"],
        "the admin API sends client_request only (ADR-0012 L34)",
    )
    invalid(
        s,
        "item-without-ids",
        with_(xc, ("target",), {"platform": "x", "kind": "post", "platform_ids": [xid]}),
        ["target", "item_ids"],
        "an item target lists item_ids (ADR-0035)",
    )
    invalid(
        s,
        "subject-in-target",
        with_(author, ("target", "author_ref"), author["author_ref"]),
        ["target", "author_ref"],
        "the subject appears once, at the top (ADR-0035)",
    )
    invalid(
        s,
        "short-form",
        {"idempotency_key": "x:post:1842957310264891392", "reason": "platform_sync"},
        ["scope"],
        "the short form with only a key goes: a deletion names its scope (ADR-0035)",
    )
    invalid(
        s,
        "withhold-without-item-ids",
        without(wh, "target", "item_ids"),
        ["target", "item_ids"],
        "an item target lists item_ids (ADR-0035)",
    )
    tolerant(s, "unknown-field", {**xc, "batch_size": 1})


def article_urls() -> None:
    s = "article.urls/v1"
    site = "3c7f9d52-1e4a-4b86-a0d3-7b2e5c8f1a90"
    feed_url = "https://www.example-daily.iq/politics/2026/10/06/budget-session"
    feed = {
        **meta(s, "news-feed-poller", "01J9N3A4K8R2T7V5X0M6C1D9HE", "2026-10-06T05:47:13Z"),
        "source_id": site,
        "url": feed_url,
        "url_key": url_key(feed_url),
        "found_via": "feed",
        "found_at": "2026-10-06T05:47:12Z",
        "title": "البرلمان يحدد موعد جلسة الموازنة",
        "published_at": "2026-10-06T05:41:00Z",
        "feed_url": "https://www.example-daily.iq/feed",
        "feed_format": "rss2",
        "provenance": prov("green", None, "news-feed-poller", "2026-10-06T05:47:12Z"),
        "retention_class": "news_excerpt",
    }
    valid(s, "prd-news-feed-poller", feed)
    r_au = [
        R_META,
        R_PROV,
        "the {envelope, payload} layout and kind: article_url go: one flat schema for every finder (ADR-0036)",
        "job_id moves to producer.job_id; access_mode leaves the message, crawl_policies holds it (ADR-0036)",
        "url_key recomputed with the one normaliser (Q9)",
    ]
    prd(
        "news-feed-poller",
        "docs/prds/news/news-feed-poller.md",
        94,
        s,
        "prd-news-feed-poller",
        r_au,
    )
    hp_url = "https://www.example-council.iq/news/20261006-session-decision"
    hp = {
        **meta(s, "news-homepage-differ", "01J9N3F1V6S4B9Y2D7K0Q8T5NA", "2026-10-06T07:03:52Z"),
        "source_id": "a82e1c47-5d3b-49f0-8e6a-2c9b7d1f0e35",
        "url": hp_url,
        "url_key": url_key(hp_url),
        "found_via": "homepage_diff",
        "found_at": "2026-10-06T07:03:51Z",
        "published_at": None,
        "provenance": prov("green", None, "news-homepage-differ", "2026-10-06T07:03:51Z"),
        "retention_class": "news_excerpt",
    }
    valid(s, "prd-news-homepage-differ", hp)
    prd(
        "news-homepage-differ",
        "docs/prds/news/news-homepage-differ.md",
        99,
        s,
        "prd-news-homepage-differ",
        [*r_au, "baseline, section_url and rank are not in ADR-0036's list and go"],
    )
    sm_url = "https://www.example-daily.iq/economy/2026/10/06/oil-exports"
    sm = {
        **meta(s, "news-sitemap-poller", "01J9N3C7P2M5Q8W1Z4T0B6F3JD", "2026-10-06T06:10:04Z"),
        "source_id": site,
        "url": sm_url,
        "url_key": url_key(sm_url),
        "found_via": "news_sitemap",
        "found_at": "2026-10-06T06:10:03Z",
        "title": "ارتفاع صادرات النفط في أيلول",
        "published_at": "2026-10-06T06:05:00Z",
        "provenance": prov("green", None, "news-sitemap-poller", "2026-10-06T06:10:03Z"),
        "retention_class": "news_excerpt",
    }
    valid(s, "prd-news-sitemap-poller", sm)
    prd(
        "news-sitemap-poller",
        "docs/prds/news/news-sitemap-poller.md",
        106,
        s,
        "prd-news-sitemap-poller",
        [*r_au, "language, publication_name and sitemap_url go (ADR-0036)"],
    )
    sh_url = "https://www.example-daily.iq/economy/2026/10/05/fiberx-wasit?utm_source=fb"
    sh_canonical = "https://www.example-daily.iq/economy/2026/10/05/fiberx-wasit"
    sh = {
        **meta(s, "search-hit-router", "01M47K8B60RM3M56CMJWGZ9C6G", "2026-10-06T03:15:02Z"),
        "source_id": "a41f7d02-93be-4c58-8e16-2b5d70c9f3e4",
        "url": sh_url,
        "url_key": url_key(sh_url),
        "found_via": "web_search",
        "found_at": "2026-10-05T03:14:09Z",
        "title": "…",
        "canonical_url": sh_canonical,
        "canonical_url_hash": url_hash(sh_canonical),
        "snippet": "…",
        "engines": ["perplexity", "gdelt"],
        "keyword_ids": ["0cd402b6-9015-45f8-86b4-d90cc086d320"],
        "client_ids": [CLIENT],
        "provenance": prov("green", "perplexity", "web-search-perplexity", "2026-10-06T03:14:08Z"),
        "retention_class": "news_excerpt",
    }
    valid(s, "prd-search-hit-router", sh)
    prd(
        "search-hit-router",
        "docs/prds/web/search-hit-router.md",
        121,
        s,
        "prd-search-hit-router",
        [
            R_PROV,
            "service and found_by go; found_via web_search and found_at from first_seen_at (ADR-0036)",
            "url_key added (ADR-0036)",
            "canonical_url_hash bare hex from the one normaliser (Q9)",
            "keyword_rule_ids give way to keyword_ids (ADR-0036)",
            "published_hint goes",
            "the provenance is the engine's that fetched the result (ADR-0003 L25)",
        ],
    )
    bf_url = "https://www.example-daily.iq/economy/2026/07/14/oil-deal"
    valid(
        s,
        "sitemap-backfill",
        {**sm, "url": bf_url, "url_key": url_key(bf_url), "found_via": "sitemap_backfill"},
    )
    cc_url = "https://www.example-daily.iq/economy/2026/09/26/fiberx-wasit"
    valid(
        s,
        "commoncrawl",
        {
            **meta(
                s, "web-commoncrawl-scanner", "01M4F72A8RQ0N3K5D2B7T4W9XB", "2026-10-09T02:20:00Z"
            ),
            "source_id": site,
            "url": cc_url,
            "url_key": url_key(cc_url),
            "found_via": "commoncrawl",
            "found_at": "2026-10-09T02:19:58Z",
            "provenance": prov("green", None, "web-commoncrawl-scanner", "2026-10-09T02:19:58Z"),
            "retention_class": "news_excerpt",
        },
    )
    metadata_invalids(s, feed)
    invalid(
        s,
        "url-key-not-the-urls",
        {
            **feed,
            "url_key": "news:url:9b1f0c6e4a7d2358e1f6a0b3c9d47e52f81a6c3b0d5e9f274a8c1b6e3d0f5a97",
        },
        ["url_key"],
        "url_key = news:url:<url_hash of the normalised URL> (ADR-0036)",
    )
    invalid(
        s,
        "canonical-hash-not-the-urls",
        {**sh, "canonical_url_hash": "9c1e4b" + "0" * 58},
        ["canonical_url_hash"],
        "the one normaliser (Q9)",
    )
    invalid(
        s,
        "found-by",
        {**sh, "found_by": "web_search"},
        ["found_by"],
        "found_by becomes found_via (ADR-0036)",
    )
    invalid(
        s,
        "kind-article-url",
        {**feed, "kind": "article_url"},
        ["kind"],
        "kind: article_url goes (ADR-0036)",
    )
    invalid(
        s,
        "unknown-found-via",
        {**feed, "found_via": "rss"},
        ["found_via"],
        "found_via is closed (ADR-0036)",
    )
    invalid(
        s,
        "prefixed-hash",
        {**sh, "canonical_url_hash": "sha256:" + url_hash(sh_canonical)},
        ["canonical_url_hash"],
        "canonical_url_hash is bare hex (ADR-0036)",
    )
    invalid(
        s,
        "article-key",
        {**feed, "idempotency_key": key("news", "article", url_hash(feed_url))},
        ["idempotency_key"],
        "no article key: the extractor derives it (ADR-0036)",
    )
    tolerant(s, "unknown-field", {**feed, "author": "فريق التحرير"})


def search_results() -> None:
    s = "search.results/v1"

    def sr(
        service: str,
        engine: str,
        job: str,
        at: str,
        fetched: str,
        query: dict[str, Any],
        result: dict[str, Any],
        canonical: str,
        raw_ref: str,
        **extra: Any,
    ) -> dict[str, Any]:
        out = {
            **meta(s, service, job, at),
            "engine": engine,
            "source_id": "7d2b0c4e-1f3a-4b5c-8d6e-9f0a1b2c3d4e",
            "keyword_ids": ["0cd402b6-9015-45f8-86b4-d90cc086d320"],
            "client_ids": [CLIENT],
            "query": query,
            "result": result,
            "canonical_url": canonical,
            "canonical_url_hash": url_hash(canonical),
            "raw_ref": raw_ref,
            "provenance": prov("green", engine, service, fetched),
            "retention_class": "news_excerpt",
        }
        out.update(extra)
        return out

    r_sr = [
        R_META,
        R_PROV,
        "keyword_rule_id becomes source_id and keyword_id keyword_ids (ADR-0037)",
        "job_id, job_kind and attempt go: producer.job_id carries the job (ADR-0037, ADR-0003)",
        "canonical_url_hash bare hex from the one normaliser (ADR-0036; Q9)",
        "raw_ref batch with six digits",
    ]
    pp = sr(
        "web-search-perplexity",
        "perplexity",
        "01M47K8B60RM3M56CMJWGZ9C6G",
        "2026-10-06T03:14:09Z",
        "2026-10-06T03:14:08Z",
        {
            "text": '"فايبر اكس" العراق',
            "variant": "arabic_context",
            "lang": "ar",
            "country": "IQ",
            "request_id": "pplx-01J9QW7",
        },
        {
            "rank": 3,
            "title": "فايبر اكس تطلق باقة جديدة في واسط",
            "url": "https://www.example-daily.iq/economy/2026/10/05/fiberx-wasit?utm_source=fb",
            "snippet": "أعلنت شركة فايبر اكس عن …",
            "date": "2026-10-05",
            "last_updated": "2026-10-05",
        },
        "https://www.example-daily.iq/economy/2026/10/05/fiberx-wasit",
        "raw/green/web/2026/10/06/web-search-perplexity/000003.jsonl.zst#17",
    )
    valid(s, "prd-web-search-perplexity", pp)
    prd(
        "web-search-perplexity",
        "docs/prds/web/web-search-perplexity.md",
        92,
        s,
        "prd-web-search-perplexity",
        [*r_sr, "the engine's truncated request_id written in full"],
    )
    mj = sr(
        "web-search-mojeek",
        "mojeek",
        "01M47P07P0M1V49VADF6SRK5BM",
        "2026-10-06T04:02:51Z",
        "2026-10-06T04:02:50Z",
        {
            "text": '"فايبر اكس" العراق',
            "variant": "arabic_context",
            "lang": "ar",
            "country": "IQ",
            "request_id": None,
        },
        {
            "rank": 5,
            "title": "فايبر اكس تطلق باقة جديدة في واسط",
            "url": "https://www.example-daily.iq/economy/2026/10/05/fiberx-wasit?utm_source=fb",
            "snippet": "أعلنت شركة فايبر اكس عن …",
            "date": "2026-10-05",
            "last_updated": None,
        },
        "https://www.example-daily.iq/economy/2026/10/05/fiberx-wasit",
        "raw/green/web/2026/10/06/web-search-mojeek/000007.jsonl.zst#41",
    )
    valid(s, "prd-web-search-mojeek", mj)
    prd(
        "web-search-mojeek",
        "docs/prds/web/web-search-mojeek.md",
        91,
        s,
        "prd-web-search-mojeek",
        r_sr,
    )
    gd = sr(
        "web-gdelt-poller",
        "gdelt",
        "01M487B1K0HD8T2YTQZB9XYNWZ",
        "2026-10-06T09:05:44Z",
        "2026-10-06T09:05:43Z",
        {
            "text": '("FiberX" OR "فايبر اكس" OR "فايبر إكس")',
            "variant": "or_group",
            "lang": None,
            "country": None,
            "request_id": None,
        },
        {
            "rank": 2,
            "title": "FiberX expands fibre network in southern Iraq",
            "url": "https://www.example-gulf-news.com/2026/10/05/fiberx-expands",
            "snippet": None,
            "date": "2026-10-05",
            "last_updated": None,
        },
        "https://www.example-gulf-news.com/2026/10/05/fiberx-expands",
        "raw/green/web/2026/10/06/web-gdelt-poller/000009.jsonl.zst#6",
        hints={
            "domain": "example-gulf-news.com",
            "language": "English",
            "source_country": "United Arab Emirates",
        },
    )
    valid(s, "prd-web-gdelt-poller", gd)
    prd(
        "web-gdelt-poller", "docs/prds/web/web-gdelt-poller.md", 94, s, "prd-web-gdelt-poller", r_sr
    )
    br = sr(
        "yt-web-search-bridge",
        "mojeek",
        "01M47F78AGDCFWH3S8DKZZJENT",
        "2026-10-06T02:03:46Z",
        "2026-10-06T02:03:44Z",
        {
            "text": 'site:youtube.com "فايبر اكس"',
            "variant": None,
            "lang": "ar",
            "country": "IQ",
            "request_id": None,
        },
        {
            "rank": 1,
            "title": "...",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "snippet": "...",
            "date": None,
            "last_updated": None,
        },
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "raw/green/web/2026/10/06/yt-web-search-bridge/000002.jsonl.zst#1",
        source_id="7b3e5f8a-1c2d-4e4f-9a6b-7c8d9e0f1a2b",
    )
    valid(s, "prd-yt-web-search-bridge", br)
    prd(
        "yt-web-search-bridge",
        "docs/prds/youtube/yt-web-search-bridge.md",
        106,
        s,
        "prd-yt-web-search-bridge",
        [
            R_META,
            R_PROV,
            "idempotency_key, platform, platform_hint, handled_by, cost and extracted go: the engines' message for all four producers (ADR-0037)",
            "the string query becomes the query object; the payload becomes the result object (ADR-0037)",
            "canonical_url and canonical_url_hash added with the one normaliser (ADR-0037 L24; Q9)",
            "keyword_ids, client_ids and raw_ref added",
            "lang ar and country IQ from the Mojeek call's lb=AR&rb=IQ (L83; ADR-0037 L24); keyword_ids the rule's enabled keyword (ADR-0044 L30)",
        ],
    )
    metadata_invalids(s, pp)
    invalid(
        s,
        "canonical-hash-not-the-urls",
        {**pp, "canonical_url_hash": "9c1e4b" + "0" * 58},
        ["canonical_url_hash"],
        "the one normaliser (Q9)",
    )
    invalid(
        s,
        "keyword-rule-id",
        {**pp, "keyword_rule_id": pp["source_id"]},
        ["keyword_rule_id"],
        "keyword_rule_id becomes source_id (ADR-0037)",
    )
    invalid(
        s,
        "job-id",
        {**pp, "job_id": "01M47K8B60RM3M56CMJWGZ9C6G"},
        ["job_id"],
        "producer.job_id carries the job (ADR-0003)",
    )
    invalid(
        s,
        "string-query",
        {**pp, "query": '"فايبر اكس" العراق'},
        ["query"],
        "query is an object (ADR-0037)",
    )
    invalid(
        s,
        "unknown-engine",
        {**pp, "engine": "google"},
        ["engine"],
        "the engines are perplexity, mojeek and gdelt (ADR-0037)",
    )
    invalid(
        s,
        "not-an-engine-service",
        {**pp, "producer": {**pp["producer"], "service": "search-hit-router"}},
        ["producer", "service"],
        "the four engines write search.results (ADR-0037)",
    )
    invalid(
        s,
        "datetime-date",
        with_(pp, ("result", "date"), "2026-10-05T00:00:00Z"),
        ["result", "date"],
        "result dates are calendar dates",
    )
    tolerant(
        s,
        "unknown-field",
        with_(pp, ("result", "favicon"), "https://www.example-daily.iq/favicon.ico"),
    )


def crawl() -> None:
    s = "crawl.policies/v1"
    base: dict[str, Any] = {
        **meta(s, "news-robots-checker", "01J9N3Q8D5W2K7X1R4T9V0MZBC", "2026-10-06T06:30:15Z"),
        "host": "www.example-daily.iq",
        "status": "allowed",
        "crawl_allowed": True,
        "reason": None,
        "access_mode": "proxy",
        "crawl_delay_seconds": 5,
        "robots_status": "ok",
        "robots_rules": {
            "group": "ListeningBot",
            "rules": {"allow": ["/wp-admin/admin-ajax.php"], "disallow": ["/wp-admin/", "/search"]},
            "sitemaps": ["https://www.example-daily.iq/sitemap_index.xml"],
            "hash": "7f3a1c9e5b2d48a6f0c1e9d7b3a5f482c6d0e1a9b7f3c5d2e8a4b6c0f1d9e373",
        },
        "usage_signals": {"search": "yes", "ai_input": "unset", "ai_train": "no"},
        "rsl": {"found": False},
        "payment": {"http_402": False, "price": None},
        "checked_at": "2026-10-06T06:30:14Z",
        "expires_at": "2026-10-07T06:30:14Z",
        "policy_version": 3,
        "changed_fields": ["access_mode"],
        "requested_by": "news-article-extractor",
        "kind": "recheck",
        "provenance": prov("green", None, "news-robots-checker", "2026-10-06T06:30:11Z"),
        "retention_class": "news_excerpt",
    }
    valid(s, "prd-news-robots-checker", base)
    prd(
        "news-robots-checker",
        "docs/prds/news/news-robots-checker.md",
        95,
        s,
        "prd-news-robots-checker",
        [
            R_META,
            "service and job_id go: producer carries them",
            "robots_rules.http_status and .fetched_at become robots_status and provenance.fetched_at; sha256 becomes hash; allow and disallow move into rules (ADR-0040, ADR-0070 b))",
            "provenance and retention_class added: the message records a fetch of robots.txt (ADR-0003)",
        ],
    )
    valid(
        s,
        "first-check",
        {
            **base,
            "kind": "first_check",
            "requested_by": None,
            "changed_fields": [],
            "policy_version": 1,
        },
    )
    valid(s, "refresh", {**base, "kind": "refresh", "requested_by": None, "changed_fields": []})
    valid(
        s,
        "ops-force",
        {**base, "kind": "ops_force", "requested_by": "person:01J9P2R4T6V8X0Z2B4D6F8H0KM"},
    )
    valid(
        s,
        "disallowed",
        {
            **base,
            "status": "disallowed",
            "crawl_allowed": False,
            "reason": "robots_disallowed",
            "access_mode": "blocked",
            "changed_fields": ["status", "crawl_allowed", "reason"],
        },
    )
    valid(
        s,
        "rsl-payment",
        {
            **base,
            "status": "paywalled",
            "crawl_allowed": False,
            "reason": "rsl_payment",
            "rsl": {
                "found": True,
                "url": "https://www.example-daily.iq/license.xml",
                "permits": ["search"],
                "prohibits": ["ai-train"],
                "payment": {"type": "per-crawl", "amount": 0.002},
            },
        },
    )
    valid(
        s,
        "robots-unreachable",
        {
            **base,
            "status": "blocked",
            "crawl_allowed": False,
            "reason": "robots_unreachable",
            "robots_status": "unavailable",
            "robots_rules": None,
        },
    )
    metadata_invalids(s, base)
    invalid(
        s,
        "allowed-with-reason",
        {**base, "reason": "challenge"},
        ["reason"],
        "reason null when allowed (news-robots-checker §5.3)",
    )
    invalid(
        s,
        "disallowed-without-reason",
        {**base, "status": "disallowed", "crawl_allowed": False},
        ["reason"],
        "a refusal names its reason",
    )
    invalid(
        s,
        "recheck-without-requester",
        {**base, "requested_by": None},
        ["requested_by"],
        "a recheck names the service that asked (F-43)",
    )
    invalid(
        s,
        "recheck-unknown-requester",
        {**base, "requested_by": "news-archive-crawler"},
        ["requested_by"],
        "a recheck's requester is a service the registry lists (F-09)",
    )
    invalid(
        s,
        "recheck-person-requester",
        {**base, "requested_by": "person:01J9P2R4T6V8X0Z2B4D6F8H0KM"},
        ["requested_by"],
        "a recheck names the service that asked, never a person (F-43)",
    )
    invalid(
        s,
        "ops-force-unknown-requester",
        {**base, "kind": "ops_force", "requested_by": "no-such-service"},
        ["requested_by"],
        "a requester that names a service is one the registry lists (Q18; F-09)",
    )
    invalid(
        s,
        "refresh-with-requester",
        {**base, "kind": "refresh"},
        ["requested_by"],
        "a refresh has no requester (F-43)",
    )
    invalid(
        s,
        "old-sha256",
        with_(base, ("robots_rules", "sha256"), base["robots_rules"]["hash"]),
        ["robots_rules", "sha256"],
        "sha256 becomes hash (ADR-0040)",
    )
    invalid(
        s,
        "nested-robots",
        {**base, "robots": {"status": "ok"}},
        ["robots"],
        "robots_status is flat (ADR-0070 b))",
    )
    invalid(
        s,
        "hyphenated-signal",
        with_(base, ("usage_signals",), {"search": "yes", "ai-input": "unset", "ai_train": "no"}),
        ["usage_signals", "ai-input"],
        "Content-Signal hyphens become underscores (ADR-0070 b))",
    )
    invalid(
        s,
        "not-the-checker",
        {**base, "producer": {**base["producer"], "service": "news-feed-poller"}},
        ["producer", "service"],
        "news-robots-checker alone writes crawl.policies (ADR-0040)",
    )
    tolerant(s, "unknown-field", {**base, "next_refresh_at": "2026-10-07T06:30:14Z"})


def dedup() -> None:
    s = "news.dedup/v1"
    k = "news:article:b81c3e5f0a2d7946e1f0c8a5d3b9e72f46a1c0d8e5b3f97a2c4d6e0b1a8f5c39"
    # The origin is news-article-extractor's article (its source and published time below), keyed
    # from its canonical URL with the helper.
    origin = article_key("https://www.example-daily.iq/politics/2026/10/06/budget-session")
    base: dict[str, Any] = {
        **meta(s, "news-dedup", "01J9N3A4K8R2T7V5X0M6C1D9HF", "2026-10-06T06:07:45Z"),
        "type": "verdict",
        "item_id": item_id(k),
        "idempotency_key": k,
        "story_id": "01J9N4W6C2R8T5K1V7X3M0DPZA",
        "is_origin": False,
        "duplicate_of": origin,
        "cluster_size": 5,
        "version": 1,
        "rank_in_cluster": 3,
        "origin_source_id": "3c7f9d52-1e4a-4b86-a0d3-7b2e5c8f1a90",
        "origin_time": "2026-10-06T05:41:00Z",
        "matched_by": "simhash",
        "hamming_distance": 2,
        "title_overlap": 0.83,
        "source_id": "a82e1c47-5d3b-49f0-8e6a-2c9b7d1f0e35",
        "decided_at": "2026-10-06T06:07:44Z",
        "provenance": prov("green", None, "news-article-extractor", "2026-10-06T06:05:10Z"),
        "retention_class": "news_excerpt",
    }
    valid(s, "prd-news-dedup", base)
    prd(
        "news-dedup",
        "docs/prds/news/news-dedup.md",
        86,
        s,
        "prd-news-dedup",
        [
            R_META,
            "service goes: producer carries it",
            "item_id added from the article's key, which store-writer writes item_stories by (ADR-0022; Q8)",
            "dedup_version becomes version, item_stories.version (Q8)",
            "provenance and retention_class copied from the article (ADR-0003)",
            "duplicate_of is news-article-extractor's article, keyed from its canonical URL with the helper (ADR-0036)",
        ],
    )
    valid(
        s,
        "origin",
        {
            **base,
            "item_id": item_id(origin),
            "idempotency_key": origin,
            "is_origin": True,
            "duplicate_of": None,
            "rank_in_cluster": 1,
            "matched_by": None,
            "hamming_distance": None,
            "title_overlap": None,
            "source_id": "3c7f9d52-1e4a-4b86-a0d3-7b2e5c8f1a90",
        },
    )
    valid(
        s,
        "story-update",
        {
            **base,
            "type": "story_update",
            "version": 2,
            "previous_story_id": "01J9N4W6C2R8T5K1V7X3M0DPZB",
        },
    )
    valid(
        s,
        "canonical-match",
        {**base, "matched_by": "canonical", "hamming_distance": None, "title_overlap": None},
    )
    metadata_invalids(s, base)
    invalid(
        s,
        "item-id-not-the-keys",
        {**base, "item_id": item_id(origin)},
        ["item_id"],
        "item_id = uuid_v5(ns_items, key) (ADR-0006)",
    )
    invalid(
        s,
        "origin-with-duplicate-of",
        {**base, "is_origin": True},
        ["duplicate_of"],
        "an origin duplicates nothing",
    )
    invalid(
        s,
        "copy-without-origin",
        {**base, "duplicate_of": None},
        ["duplicate_of"],
        "a copy names its origin",
    )
    invalid(
        s,
        "dedup-version",
        {**base, "dedup_version": 1},
        ["dedup_version"],
        "dedup_version becomes version (Q8)",
    )
    invalid(
        s,
        "unknown-match",
        {**base, "matched_by": "minhash"},
        ["matched_by"],
        "matched_by is closed (Q8)",
    )
    tolerant(s, "unknown-field", {**base, "simhash": "f3a1c9e5b2d48a6f"})


def run() -> None:
    normalized()
    hits()
    discovery()
    profiles()
    analysis()
    metrics_topic()
    deletions()
    article_urls()
    search_results()
    crawl()
    dedup()
    _ = (json, ROOT, ulid_for, candidate_key_from_id)
