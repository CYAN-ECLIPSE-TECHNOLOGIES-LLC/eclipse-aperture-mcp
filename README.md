# Eclipse Aperture MCP

**Powered by Cyan Eclipse Technologies** — https://cetech.ai

**Eclipse Aperture — the Instagram adapter: one approved package becomes native Feed, Carousel, Story, and Reel variants for a professional account, with publishing and analytics only through Meta's sanctioned Graph API surface.**

## Why this exists

The White Report already operates Instagram professionally through the house's existing sanctioned connector. S0 turns that working route into a capability-probed, hash-bound product surface instead of a collection of habits (spec §9, §18). Aperture is that surface: the capability declaration, the native variants, the preview the owner approves, and the receipts.

## Status — honest labels

v0.1.0, phase **S0 formalization**. **This server posts nothing and makes no live calls.** The house's Instagram operation continues through its existing connector, *outside* this product; Aperture references that route and never duplicates it — there is no second token path, no session handling, and no credential material anywhere in this code. Local stdio, Python stdlib only. **No certification claimed — bench pending.**

## Tools (4)

| Tool | What it does |
|---|---|
| `capability_probe` | Returns the capability matrix from a **static declaration fixture** (dated 2026-10-25, `[verify]`-flagged): `PUBLISH_API` for publishing/drafts, `READ_API` for reads, `OWN_ENGAGEMENT_API` for own-media comments, `COMMUNITY_PREP` for community engagement — the §9 posture for eligible professional accounts, grade A subject to Meta app permissions, review, account role, and current Graph API version. `simulate_probe_failure=true` exercises the family downgrade rule: write modes collapse to prep — automatically, and never to a workaround. |
| `variant_build` | Build one native variant from a canonical package: **Feed 4:5**, **Carousel** in narrative order (first card = hook, payoff before end card), **Reel 9:16**, **Story 9:16** — with the working link path (profile link; Story link sticker — **caption links are not clickable and are never the conversion path**), the platform AI-media label carried on the variant, classified diffs vs canonical, and the variant hash. |
| `preview_pack` | The exact native preview the owner approves: rendered geometry, caption, link path, safe-zone notes, hashtags, disclosures, order — plus diffs and the hashes an approval binds. |
| `receipt_list` | The append-only, hash-chained receipt ledger, with chain verification. |

## Native rules carried in code (§9)

- Feed portrait **4:5** uses the grid better than square; landscape derivatives are shown, never center-cropped blindly.
- Reels/Stories **9:16** with platform safe zones respected — text and evidence stay out of the top/bottom UI bands.
- Hashtags are searchable metadata, not stuffing; the approved set appears in the diff.
- Threads is **not** a separate product (§8): it rides as a sub-adapter inside this Meta family tooling when its gated modes are proven — no Threads listing or claim exists.

## Run it

```bash
python3 server.py            # MCP over stdio, stdlib only, no dependencies
python3 smoke.py             # probe + Reel variant + preview over real stdio
python3 -m unittest discover tests   # 11 tests
```

State persists in `data/state.json` (override with `ECLIPSE_APERTURE_STATE`). `data/` is gitignored. The capability fixture lives at `fixtures/capability.json`; the smoke drives the social core's `sample_content.json` package.

## Roadmap (per spec §21)

- Dated Meta terms/capability record replacing the static declaration → live `ig_capability_probe`.
- `ig_media_stage` / `ig_container_verify` / `ig_publish_receipt` / `ig_insights_read` / `ig_own_comment_queue` — only against the sanctioned Graph surface, only for approved hash-bound packs, with publish read-back before any completion claim. Execution wiring stays on the house's existing route.

## License / attribution

A Cyan Eclipse Technologies product. The "Powered by Cyan Eclipse Technologies" attribution travels with it.
