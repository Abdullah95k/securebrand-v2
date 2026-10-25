"""Writes fixtures/contracts/<schema>/{valid,invalid,tolerant}/ and the PRD manifest (F2, A4 to A6)."""

import shutil

import common
import control_topics
import data_topics
import n8n_topics
import raw_items

KEEP = {"golden", "README.md"}

for child in common.ROOT.iterdir():
    if child.name in KEEP:
        continue
    if child.is_dir():
        shutil.rmtree(child)
    else:
        child.unlink()

raw_items.run()
data_topics.run()
control_topics.run()
n8n_topics.run()
common.finish()
print(f"wrote {len(common.WRITTEN)} fixtures, {len(common.MANIFEST)} manifest entries")
