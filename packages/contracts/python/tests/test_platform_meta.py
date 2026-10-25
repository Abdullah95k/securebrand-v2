"""A25: platform_meta keys per platform and source type (ADR-0065 c), ADR-0013 c), ADR-0041)."""

from typing import Any

from listening_contracts.validate import ValidationResult, validate

from conftest import fixture

ID = "registry.decisions/v1"
CASES: list[tuple[str, str, dict[str, Any]]] = [
    ("youtube", "channel", {"uploads_playlist_id": "UUx3Kp9vQ2mLwR7tYb4nJ8sA"}),
    ("instagram", "hashtag", {"ig_user_id": "17841400112233445"}),
    (
        "telegram",
        "group",
        {
            "linked_channel_source_id": "8a3f1c6e-2b9d-4e70-b5a4-f0c9d2e1b7a8",
            "linked_chat_id": "-1001987650000",
        },
    ),
]


def fails_at(result: ValidationResult, path: list[str | int]) -> bool:
    return not result.ok and path in [i["path"] for i in result.issues]


def add_with(platform: str, source_type: str, meta: dict[str, Any]) -> dict[str, Any]:
    value = fixture(ID, "valid", "add-telegram-group.json").copy()
    value["add"]["source"].update(
        {"platform": platform, "source_type": source_type, "platform_meta": meta}
    )
    return value


def test_accepts_each_platforms_keys() -> None:
    for platform, source_type, meta in CASES:
        assert validate(ID, add_with(platform, source_type, meta)).issues == [], platform
    assert validate(ID, fixture(ID, "valid", "add-keyword.json").value).ok
    event = fixture("source.events/v1", "valid", "push-coverage-change.json").value
    assert validate("source.events/v1", event).ok


def test_rejects_another_platforms_key() -> None:
    for platform, source_type, _ in CASES:
        for other, _type, meta in CASES:
            if other == platform:
                continue
            for key, v in meta.items():
                result = validate(ID, add_with(platform, source_type, {key: v}))
                assert fails_at(result, ["add", "source", "platform_meta", key]), (key, platform)
    page = validate(ID, add_with("facebook", "page", {"ig_user_id": "1"}))
    assert fails_at(page, ["add", "source", "platform_meta", "ig_user_id"])
    event = fixture("source.events/v1", "valid", "prd-registry-writer.json").copy()
    event["platform_meta"] = {"uploads_playlist_id": "UUx3"}
    assert fails_at(validate("source.events/v1", event), ["platform_meta", "uploads_playlist_id"])
