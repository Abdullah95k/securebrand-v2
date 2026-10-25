import json
import subprocess
import sys

from conftest import PACKAGE_DIR, golden


def test_every_helper_returns_the_same_output_for_the_same_input_in_a_fresh_process_and_in_the_other_language_the_golden_files_are_the_shared_record() -> (  # noqa: E501 - the twin of the TypeScript test's name
    None
):
    keys = golden("keys.json")["keys"]
    urls = golden("urls.json")["urls"]
    script = """
import json, sys
from listening_contracts.keys import idempotency_key, item_id
from listening_contracts.url import url_hash
data = json.load(sys.stdin)
out = {
    "keys": [
        {"key": k, "item_id": item_id(k)}
        for k in (idempotency_key(i["platform"], i["kind"], i["platform_id"]) for i in data["keys"])
    ],
    "urls": [url_hash(u, b) for u, b in data["urls"]],
}
print(json.dumps(out))
"""
    payload = json.dumps(
        {"keys": [k["input"] for k in keys], "urls": [[u["input"], u.get("base")] for u in urls]}
    )
    run = subprocess.run(
        [sys.executable, "-c", script],
        input=payload,
        capture_output=True,
        text=True,
        check=True,
        cwd=PACKAGE_DIR,
    )
    out = json.loads(run.stdout)
    assert out["keys"] == [{"key": k["key"], "item_id": k["item_id"]} for k in keys]
    assert out["urls"] == [u["url_hash"] for u in urls]
