# ADR-0068 · AI and media use of platform content: a register of permitted uses

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, F3, A0, analysis-sentiment, analysis-topics, analysis-entities, analysis-media, normalize-item, raw-archiver, deletion-propagator, news-robots-checker, news-article-extractor, D3 (the admin console), and every fetch service that downloads media: the lanes Fetch posts, Comments and Comments and stats
Source: D2-Q068 (user decision; changed by the user's answer) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

Three analysis PRDs ask the same question: "May each platform's content and vendor data be used to train and evaluate in-house models, and for how long? Legal to confirm" (`analysis-sentiment §14 Q3`; the same in `analysis-entities §14 Q7` and `analysis-topics §14 Q7`). A0 freezes train, dev and test splits from staging samples (A0 brief, "Builds"). The terms in CONVENTIONS pull different ways: Meta's Tech Provider "processes only on behalf of its client" (L163); TikTok forbids databases on individuals (L178); LinkedIn keeps member data 48 hours (L192); Instagram allows only "aggregated, de-identified output" (L171); news is stored as excerpts under Law No. 3 of 1971 (L213). The news PRDs ask whether Content-Signal `search = no` is a stop (`news-robots-checker §14 Q1`, proposed yes) and what `ai-input = no` does to model analysis (`news-robots-checker §14 Q2`, `news-article-extractor §14 Q2`). analysis-media asks whether media may be stored, and whether YouTube thumbnails only is right (`analysis-media §14 Q2`), as README decision 7 proposes "pending legal review" (`README L184`).

The user's answer, 7 Oct 2026: "Q068 we will download some of the content and if it does not break any rules then we will use it for training as well." The register was the orchestrator's reading of that answer, relayed to the user on 7 Oct 2026: evaluation sets as (a) and Content Signals as (c), as proposed; training and downloads governed by a register of permitted uses, whose entries the user or the user's compliance owner sets, each "not allowed" until set. On 9 Oct 2026 the user changed its default: "Allowed by default". A use (training on a source's content; downloading its images, audio or video) is allowed unless the register says it is not, and `ai-train = no` still always excludes a host. The orchestrator reads the 7 Oct words "if it does not break any rules" to mean that the register is seeded with "not allowed" rows for every use a platform's terms or a vendor contract already forbids. YouTube's terms forbid downloading video, so YouTube stays thumbnails only (`D2-SUMMARY.md`, "Answers", the follow-up of 9 Oct 2026).

Settles: analysis-entities §14 Q7, analysis-media §14 Q2, analysis-sentiment §14 Q3, analysis-topics §14 Q7, news-article-extractor §14 Q2, news-robots-checker §14 Q1, news-robots-checker §14 Q2.

## Options

1. **Evaluate on de-identified platform content; train only on data cleared for training; honour Content Signals; store media only where the terms allow.** _Taken for (a) and (c); its (b) and (d), which waited for counsel source by source, give way to a register of permitted uses, and so does the variant of (d): the register, not the team's reading of the terms, says where media may be downloaded (see Decision)._
   - (a) Evaluation: A0's dev and test sets may hold de-identified platform items (author references only, ADR-0010), never shared outside the service. A frozen split outlives some classes (CONVENTIONS L75 to L77), so only these may enter: `meta_on_request`, `vendor_agreed`, `tiktok_display`, `telegram_bot` and `news_excerpt` (the excerpt, never cached full text); `x_24h_sync` items only because deletions reach the set within 24 hours; `youtube_30d_text` items with their comment text only until day 30, after which the split keeps the id and the label; no `linkedin_48h` or `linkedin_org` item at all. The sets are registered holders in the SDK purge registry (ADR-0035), and A0 re-versions a split when a deletion removes one of its items. The splits committed under `fixtures/eval/` (A0 brief) hold ids and labels only; the text sits in the registered store, so no deletion rewrites git history.
   - (b) Training and fine-tuning without counsel: licensed or public datasets, and synthetic and annotator-written examples. Everything else waits for counsel's confirmation source by source (`DEFERRED.md`, owners A1 to A4): platform content from Meta, TikTok, X, LinkedIn and YouTube; client-owned content, Meta's included, since a model shared by all clients is not processing "on behalf of its client" (L163), consent or not; news text, kept as excerpts for copyright (L213), where a missing `ai-train = no` is not a licence; Telegram data from the bot and the vendor; Disqus comments; and vendor data, whose platform's terms still apply. `ai-train = no` always keeps a host's text out.
   - (c) Content Signals: `search = no` means no article fetch and no excerpt stored for that host, while the site row stays (news-robots-checker's proposal); `ai-input = no` keeps that host's excerpts and cached text out of model analysis while keyword matching still runs; `ai-train = no` as in (b). news-article-extractor already carries `usage_signals` in the raw envelope's `context` (`news-article-extractor §6.2 L103-L104`, ADR-0005); normalize-item copies it into a declared field of `items.normalized`, which F2 adds, so the analysis services can skip the item.
   - (d) Media: images are stored under `media/<sha256>` only where the platform's terms and the vendor contract allow, under the item's retention class; YouTube stays thumbnails only in v1 (README decision 7); audio and video are downloaded nowhere until counsel confirms per platform. So analysis-media runs on images and thumbnails only in v1: no speech-to-text and no video-frame OCR (`analysis-media §3 L23`, `§5.2 L54`, `§13 L156`); A4 builds them behind a setting left off.

   Consequences: A0 starts on real Iraqi samples after G2, with no LinkedIn items; models are fine-tuned on public and annotated data at first; video analysis waits for counsel.

   Variant of (d): the no-download rule stays YouTube-only, as README decision 7 wrote it, and other platforms' audio and video are downloaded "where the terms allow" like images. Consequences: speech-to-text and frame OCR run in v1 where the team reads the terms as allowing it, before counsel confirms.

2. **Train and evaluate on all collected content, de-identified, within each item's retention class.** _Not taken: training uses only what the register permits._ Consequences: the best dialect models soonest, but an exposure under Meta's "on behalf of its client" and TikTok's database rule that counsel may force the platform to unwind, with retraining.
3. **No platform content in any model set,** evaluation included. _Not taken._ Consequences: no exposure, but an evaluation set unlike the data clients see; A0's plan changes.

## Decision

Evaluation sets follow (a) and Content Signals (c), as proposed. Training and media downloads follow a register of permitted uses: platform, vendor, client-owned, news and Telegram content may train models, and images, audio and video may be downloaded, wherever the register's entry for that source says its terms allow it. The user or the user's compliance owner sets the entries; an entry defaults to "not allowed", and `ai-train = no` always excludes a host.

**(a) Evaluation, as proposed**

- A0's dev and test sets may hold de-identified platform items (author references only, ADR-0010), never shared outside the service. A frozen split outlives some classes (CONVENTIONS L75 to L77), so only these may enter: `meta_on_request`, `vendor_agreed`, `tiktok_display`, `telegram_bot` and `news_excerpt` (the excerpt, never cached full text); `x_24h_sync` items only because deletions reach the set within 24 hours; `youtube_30d_text` items with their comment text only until day 30, after which the split keeps the id and the label; no `linkedin_48h` or `linkedin_org` item at all. The sets are registered holders in the SDK purge registry (ADR-0035), and A0 re-versions a split when a deletion removes one of its items. The splits committed under `fixtures/eval/` (A0 brief) hold ids and labels only; the text sits in the registered store, so no deletion rewrites git history.

**(b) Training, by the register**

- Licensed or public datasets, and synthetic and annotator-written examples, may train and fine-tune models without an entry.
- Platform, vendor, client-owned, news and Telegram content may be used for training when the register's entry for that source says the source's terms allow it. Until an entry says so, the source's content stays out of every training set.
- `ai-train = no` always excludes a host's text, whatever its entry says.
- A training set that holds platform content is a registered holder in the SDK purge registry, like the evaluation sets (ADR-0035).

**(c) Content Signals, as proposed**

- `search = no` means no article fetch and no excerpt stored for that host, while the site row stays (news-robots-checker's proposal); `ai-input = no` keeps that host's excerpts and cached text out of model analysis while keyword matching still runs; `ai-train = no` as in (b). news-article-extractor already carries `usage_signals` in the raw envelope's `context` (`news-article-extractor §6.2 L103-L104`, ADR-0005); normalize-item copies it into a declared field of `items.normalized`, which F2 adds, so the analysis services can skip the item.

**(d) Downloads, by the register**

- Images, audio and video are downloaded wherever the register says the platform's terms and the vendor contract allow it, and stored under `media/<sha256>` through raw-archiver's media endpoint (ADR-0039), under the item's retention class.
- YouTube stays thumbnails only unless the register says otherwise, because YouTube's terms forbid downloading video without YouTube's prior written permission (and the rights holders', where they apply); an entry that allows it names that permission as the clause relied on. This is the legal review README decision 7 left pending (`README L184`).
- Speech-to-text and frame OCR run on media that was downloaded under the register; A4 builds them in v1, and they process nothing the register did not allow.

**The register of permitted uses**

- It lives in the control plane as an F3 table, `permitted_uses`: one row per subject (each platform, Disqus included, each vendor and each news host) and use (training; downloading images, audio or video), with whether the use is allowed (false by default, and false for a missing row), the terms or contract clause relied on, and who set it and when.
- Its owner is the admin console, which writes it audited (D3 specifies the writer); the user, or the user's compliance owner, sets every entry.
- Services read it through the SDK: the training pipelines of A1 to A4 before a source's content enters a training set, and every service that downloads media (analysis-media and the fetch services, `raw-archiver §3 L29`) before each download.

Why: The user wants content downloaded and used for training wherever that breaks no rule. A register makes "no rule broken" a recorded decision per source, made by the user or the compliance owner, rather than a reading each build session makes; defaulting to "not allowed" keeps everything out until someone has checked. Evaluation on de-identified samples and the Content Signals stay as proposed.

## Consequences

Models can train on real Iraqi content as soon as the register allows a source; media analysis covers what the register allows, YouTube thumbnails from the start; until an entry allows it, no source's content trains a model and no media beyond YouTube thumbnails is downloaded.

- CONVENTIONS v1.1, "Security and compliance in every service": the evaluation rule, training and downloads by the register, the three Content-Signal rules and the media rule; `permitted_uses` among the control-plane tables.
- F3 creates `permitted_uses`; F2 adds the declared `usage_signals` field to `items.normalized`; D3 specifies the admin console's register screen.
- A0 starts on real samples after G2, with no LinkedIn items; A1 to A4 train on public and annotated data first, then on the sources the register allows; A4 builds speech-to-text and frame OCR in v1.
- `DEFERRED.md`: filling the register, owned by the user (or the user's compliance owner), before any training on platform content and any download beyond YouTube thumbnails; with each entry, what deleting a training item requires of a model already trained on it.

Sessions that must read this: F2 (the declared `usage_signals` field on `items.normalized`), A0 (its splits need only D2, A0 brief), then C4, C13, A1, A2, A3, A4, N1, N6, F3, D3.
