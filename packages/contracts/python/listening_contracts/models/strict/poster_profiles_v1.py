# Generated from schemas/poster.profiles/v1.json by scripts/gen_python.py (strict). Do not edit.

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel
from pydantic.experimental.missing_sentinel import MISSING


class Followers(RootModel[int]):
    root: Annotated[int, Field(ge=0, le=9007199254740991)]


class ClientId(RootModel[str]):
    root: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]


class CachedUntil(RootModel[str]):
    root: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class SourceId(RootModel[str]):
    root: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]


class PlatformId(RootModel[str]):
    root: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]


class Handle(RootModel[str]):
    root: Annotated[str, Field(min_length=1)]


class Url(RootModel[str]):
    root: Annotated[str, Field(pattern="^https?:\\/\\/[^\\x00-\\x20]+$")]


class Posts30d(RootModel[int]):
    root: Annotated[int, Field(ge=0, le=9007199254740991)]


class LastPostAt(RootModel[str]):
    root: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class PostsPerDay(RootModel[float]):
    root: Annotated[float, Field(ge=0.0)]


class DuplicateTextShare(RootModel[float]):
    root: Annotated[float, Field(ge=0.0, le=1.0)]


class AccountCreatedAt(RootModel[str]):
    root: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class KeywordId(RootModel[str]):
    root: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]


class Vendor(RootModel[str]):
    root: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]


class Producer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    service: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]
    version: Annotated[str, Field(max_length=64, pattern="^[^\\x00-\\x20]+$")]
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]


class Provenance(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route: Literal["green", "amber"]
    vendor: Vendor | None
    service: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]
    fetched_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class SignalEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    signal: Literal[
        "iraqi_place", "platform_country_iq", "phone_964", "iq_domain", "outlet_link", "seed_list"
    ]
    matched: Annotated[str, Field(min_length=1)]
    where: Annotated[str, Field(min_length=1)]


class LangShare(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ar: Annotated[float, Field(ge=0.0, le=1.0)]
    ckb: Annotated[float, Field(ge=0.0, le=1.0)]
    en: Annotated[float, Field(ge=0.0, le=1.0)]
    mixed: Annotated[float, Field(ge=0.0, le=1.0)]
    other: Annotated[float, Field(ge=0.0, le=1.0)]
    und: Annotated[float, Field(ge=0.0, le=1.0)]
    ar_iraqi: Annotated[float, Field(ge=0.0, le=1.0)]
    sample: Annotated[int, Field(ge=0, le=9007199254740991)]


class WebsiteDomain(RootModel[str]):
    root: Annotated[
        str, Field(pattern="^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*\\.?$")
    ]


class PageLocation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    city: str | None
    country: str | None


class Growth(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subscribers_30d: Annotated[int, Field(ge=-9007199254740991, le=9007199254740991)]


class NewsSitemap(RootModel[str]):
    root: Annotated[str, Field(pattern="^https?:\\/\\/[^\\x00-\\x20]+$")]


class Sitemap(RootModel[str]):
    root: Annotated[str, Field(pattern="^https?:\\/\\/[^\\x00-\\x20]+$")]


class ArticleUrlPattern(RootModel[str]):
    root: Annotated[str, Field(min_length=1)]


class CommentsProvider(RootModel[str]):
    root: Annotated[str, Field(min_length=1)]


class DisqusShortname(RootModel[str]):
    root: Annotated[str, Field(min_length=1)]


class LastArticleAt(RootModel[str]):
    root: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class NewestAt(RootModel[str]):
    root: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class Feed(BaseModel):
    model_config = ConfigDict(extra="forbid")
    url: Annotated[str, Field(pattern="^https?:\\/\\/[^\\x00-\\x20]+$")]
    format: Annotated[str, Field(min_length=1)]
    items: Annotated[int, Field(ge=0, le=9007199254740991)]
    newest_at: NewestAt | None
    has_body: bool


class IndividualProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["poster.profiles/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
    status: Literal["resolved", "review", "unresolvable"]
    reason: (
        Literal[
            "age_gated",
            "not_indexed",
            "unclassified",
            "ambiguous",
            "schema_unknown",
            "grant_missing",
            "not_found",
            "private",
            "suspended",
            "protected",
        ]
        | None
    )
    followers: Followers | None
    verified: bool | None
    client_ids: list[ClientId]
    resolved_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    cached: bool
    cached_until: CachedUntil | None
    provenance: Provenance
    retention_class: Literal[
        "meta_on_request",
        "vendor_agreed",
        "x_24h_sync",
        "news_excerpt",
        "telegram_bot",
        "tiktok_display",
        "linkedin_48h",
        "linkedin_org",
        "youtube_30d_text",
    ]
    author_ref: Annotated[str, Field(pattern="^[0-9a-f]{64}$")]
    account_type: Literal["individual"]
    individual: Literal[True]
    public_account: Literal[False]


class CountrySignals(BaseModel):
    model_config = ConfigDict(extra="forbid")
    iraqi_place: bool
    platform_country_iq: bool
    phone_964: bool
    iq_domain: bool
    outlet_link: bool
    seed_list: bool
    signal_evidence: list[SignalEvidence]


class SiteProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    feeds: list[Feed]
    news_sitemap: NewsSitemap | None
    sitemaps: list[Sitemap]
    homepage_diff: bool
    article_url_patterns: list[ArticleUrlPattern]
    comments_provider: CommentsProvider | None
    disqus_shortname: DisqusShortname | None
    access_mode: Literal["direct", "headless", "proxy", "blocked"]
    articles_per_day_estimate: Annotated[float, Field(ge=0.0)]
    last_article_at: LastArticleAt | None


class Extras(BaseModel):
    model_config = ConfigDict(extra="forbid")
    category: Annotated[str | MISSING, Field(min_length=1)] = MISSING
    location: PageLocation | MISSING = MISSING
    website_domains: list[WebsiteDomain] | MISSING = MISSING
    about: str | MISSING = MISSING
    media_count: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    biography: str | MISSING = MISSING
    website: Annotated[str | MISSING, Field(pattern="^https?:\\/\\/[^\\x00-\\x20]+$")] = MISSING
    video_count: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    region: Annotated[str | MISSING, Field(min_length=1)] = MISSING
    bio: str | MISSING = MISSING
    bio_link: Annotated[str | MISSING, Field(min_length=1)] = MISSING
    following: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    location_text: str | MISSING = MISSING
    description: str | MISSING = MISSING
    url_domain: Annotated[
        str | MISSING,
        Field(pattern="^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*\\.?$"),
    ] = MISSING
    account_age_days: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    posts_sampled: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    growth: Growth | MISSING = MISSING
    country: Annotated[str | MISSING, Field(pattern="^[A-Z]{2}$")] = MISSING
    country_source: Literal["snippet", "brandingSettings"] | MISSING = MISSING
    default_language: Annotated[str | MISSING, Field(min_length=1)] = MISSING
    view_count: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    published_at: Annotated[
        str | MISSING,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ] = MISSING
    uploads_playlist_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    made_for_kids: bool | MISSING | None = MISSING
    description_lang: Literal["ckb", "ar", "other", "none"] | MISSING = MISSING
    host: Annotated[
        str | MISSING,
        Field(pattern="^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*\\.?$"),
    ] = MISSING
    site_profile: SiteProfile | MISSING = MISSING
    proposed_tier: Literal[1, 2, 3] | MISSING = MISSING
    discovered_by: Annotated[str | MISSING, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")] = MISSING
    crawl_allowed: bool | MISSING = MISSING


class Profile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["poster.profiles/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
    status: Literal["resolved", "review", "unresolvable"]
    reason: (
        Literal[
            "age_gated",
            "not_indexed",
            "unclassified",
            "ambiguous",
            "schema_unknown",
            "grant_missing",
            "not_found",
            "private",
            "suspended",
            "protected",
        ]
        | None
    )
    followers: Followers | None
    verified: bool | None
    client_ids: list[ClientId]
    resolved_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    cached: bool
    cached_until: CachedUntil | None
    provenance: Provenance
    retention_class: Literal[
        "meta_on_request",
        "vendor_agreed",
        "x_24h_sync",
        "news_excerpt",
        "telegram_bot",
        "tiktok_display",
        "linkedin_48h",
        "linkedin_org",
        "youtube_30d_text",
    ]
    candidate_key: Annotated[
        str,
        Field(
            pattern="^(facebook:group:[0-9]+|news:site:[a-z0-9-]+(\\.[a-z0-9-]+)+|(facebook|instagram|tiktok|x|telegram|youtube):[^\\x00-\\x20:]+|linkedin:[^\\x00-\\x20]+)$"
        ),
    ]
    source_id: SourceId | None
    source_type: (
        Literal[
            "page",
            "group",
            "account",
            "creator",
            "channel",
            "company_page",
            "site",
            "hashtag",
            "keyword_rule",
        ]
        | None
    )
    account_type: (
        Literal[
            "page",
            "group",
            "business",
            "organization",
            "channel",
            "company_page",
            "site",
            "creator",
            "public_figure",
            "individual",
            "business_or_creator",
            "organization_or_public_figure",
        ]
        | None
    )
    individual: bool | None
    public_account: bool | None
    platform_id: PlatformId | None
    handle: Handle | None
    url: Url | None
    display_name: str | None
    posts_30d: Posts30d | None
    last_post_at: LastPostAt | None
    posts_per_day: PostsPerDay | None
    duplicate_text_share: DuplicateTextShare | None
    default_avatar: bool | None
    account_created_at: AccountCreatedAt | None
    owned_by_client: bool | None
    country_signals: CountrySignals | None
    lang_share: LangShare | None
    keyword_ids: list[KeywordId]
    route: Literal["green", "amber"] | None
    vendor: Vendor | None
    review_flags: list[Literal["watchlist_only", "hidden_subscriber_count", "made_for_kids"]]
    extras: Extras | MISSING = MISSING
    post_count: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    origin: Literal["discovery", "manual"] | MISSING = MISSING
    proposed_source_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING


class PosterProfilesV1(RootModel[IndividualProfile | Profile]):
    root: Annotated[IndividualProfile | Profile, Field(title="PosterProfilesV1")]
