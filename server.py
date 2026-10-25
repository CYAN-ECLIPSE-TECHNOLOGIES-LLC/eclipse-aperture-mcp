#!/usr/bin/env python3
"""Eclipse Aperture MCP — v0.1.0, phase S0 (formalization).

Powered by Cyan Eclipse Technologies (cetech.ai).

Eclipse Aperture — the Instagram adapter: one approved package becomes
native Feed, Carousel, Story, and Reel variants for a professional
account, with publishing and analytics only through Meta's sanctioned
Graph API surface. (Spec: eclipse-social-family-spec-20261025.md SS9.)

V0.1 IS A FORMALIZATION, NOT A SECOND INSTAGRAM PIPE. The house
already operates Instagram through its existing sanctioned connector;
that route stays where it is and is REFERENCED here, never duplicated.
This server codes the governed wrapper around it:

  * capability_probe — a STATIC capability declaration (fixture,
    dated, [verify]-flagged). v0.1 makes NO live Graph API calls.
    A simulated probe failure downgrades the declared modes exactly
    as the family core prescribes (writes collapse to prep).
  * variant_build — native Feed (4:5) / Carousel (narrative order) /
    Reel (9:16) / Story (9:16) variants from a canonical package,
    each hash-bound, each with its classified diff vs canonical.
  * preview_pack — the exact native preview + diffs the owner
    approves: geometry, caption, the working link path (Instagram
    captions carry no clickable link — the profile link / Story
    sticker is the path), safe-zone notes, disclosure labels.
  * receipt_list — the hash-chained receipt ledger.

NO posting, NO engagement action, NO credential material exists in
this server. Approval here binds hashes; execution happens only
through the house's existing sanctioned route, outside this product.

Transport: MCP over stdio (newline-delimited JSON-RPC 2.0), stdlib only.
State file: $ECLIPSE_APERTURE_STATE or ./data/state.json beside here.
Capability declaration: fixtures/capability.json beside here.
"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
STATE_PATH = Path(os.environ.get(
    "ECLIPSE_APERTURE_STATE", ROOT / "data" / "state.json"))
CAPABILITY_PATH = ROOT / "fixtures" / "capability.json"

DOWNGRADE = {"PUBLISH_API": "PREP_PACK", "DRAFT_API": "PREP_PACK",
             "OWN_ENGAGEMENT_API": "COMMUNITY_PREP",
             "COMMUNITY_API_PILOT": "COMMUNITY_PREP",
             "READ_API": "READ_API", "PREP_PACK": "PREP_PACK",
             "COMMUNITY_PREP": "COMMUNITY_PREP"}

SURFACES = {
    "feed": {"aspect": "4:5", "links_clickable": False,
             "link_placement": "profile_link",
             "safe_zones": "Feed portrait 4:5; hook lives in the first "
                           "lines of caption; grid crop is center 1:1 — "
                           "keep the claim inside it.",
             "char_limit": 2200},
    "carousel": {"aspect": "4:5", "links_clickable": False,
                 "link_placement": "profile_link",
                 "safe_zones": "Card order is narrative order: first "
                               "card carries the hook, payoff card "
                               "precedes any end card.",
                 "char_limit": 2200},
    "reel": {"aspect": "9:16", "links_clickable": False,
             "link_placement": "profile_link",
             "safe_zones": "9:16; keep text/evidence out of the top "
                           "and bottom UI bands; captions per the "
                           "approved master workflow.",
             "char_limit": 2200},
    "story": {"aspect": "9:16", "links_clickable": True,
              "link_placement": "story_link_sticker",
              "safe_zones": "9:16; keep text/evidence out of the top "
                            "and bottom UI bands; link sticker is "
                            "the one clickable surface.",
              "char_limit": 2200},
}


class ToolError(Exception):
    pass


def now() -> int:
    return int(time.time())


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


# --------------------------------------------------------------------- state
def empty_state() -> dict:
    return {"variants": {}, "last_probe": None, "receipts": []}


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return empty_state()


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=1))


def emit_receipt(state: dict, rtype: str, detail: dict) -> dict:
    prev = state["receipts"][-1]["hash"] if state["receipts"] else "GENESIS"
    entry = {"seq": len(state["receipts"]) + 1, "ts": now(), "type": rtype,
             "prev_hash": prev, "detail": detail}
    entry["hash"] = sha(prev + canon({k: v for k, v in entry.items()
                                      if k != "hash"}))
    state["receipts"].append(entry)
    return entry


def verify_receipt_chain(receipts) -> bool:
    prev = "GENESIS"
    for e in receipts:
        if e.get("prev_hash") != prev:
            return False
        expect = sha(prev + canon({k: v for k, v in e.items() if k != "hash"}))
        if e.get("hash") != expect:
            return False
        prev = e["hash"]
    return True


# --------------------------------------------------------------- capability
def load_declaration() -> dict:
    return json.loads(CAPABILITY_PATH.read_text())


def run_probe(simulate_failure: bool) -> dict:
    decl = load_declaration()
    declared = decl["modes"]
    if simulate_failure:
        effective = {cap: DOWNGRADE.get(m, m)
                     for cap, m in declared.items()}
        status = "failed"
    else:
        effective = dict(declared)
        status = "ok"
    return {"probe_type": "static_declaration",
            "live_calls_made": False,
            "status": status,
            "declared_at": decl["declared_at"],
            "platform": decl["platform"],
            "grade": decl["grade"],
            "graph_api_version": decl["graph_api_version"],
            "verify_flags": decl["verify_flags"],
            "declared_modes": declared,
            "effective_modes": effective,
            "downgraded": effective != declared,
            "note": ("STATIC declaration fixture — v0.1 probes no live "
                     "Graph endpoint. Modes are the spec SS9 posture "
                     "for eligible professional accounts, [verify] "
                     "against a dated capability record at build-out. "
                     + ("Simulated failure: effective modes downgraded; "
                        "a downgrade never triggers a workaround."
                        if simulate_failure else
                        "Declaration accepted at face value for "
                        "formalization purposes."))}


def t_capability_probe(state, args):
    probe = run_probe(bool(args.get("simulate_probe_failure", False)))
    state["last_probe"] = probe
    r = emit_receipt(state, "capability_probe",
                     {"status": probe["status"],
                      "downgraded": probe["downgraded"],
                      "probe_type": probe["probe_type"]})
    return {**probe, "receipt_seq": r["seq"]}


def effective_modes(state) -> dict:
    if state.get("last_probe"):
        return state["last_probe"]["effective_modes"]
    return run_probe(False)["effective_modes"]


# ------------------------------------------------------------------ variants
HASHED_FIELDS = ("variant_id", "canonical_id", "canonical_hash",
                 "surface", "destination_account", "media", "copy_text",
                 "link", "hashtags", "disclosures_out", "order",
                 "schedule")


def variant_hash(variant: dict) -> str:
    return sha(canon({k: variant.get(k) for k in HASHED_FIELDS}))


def content_hash_of(package: dict) -> str:
    fields = ("canonical_id", "title", "body", "short_copy", "long_copy",
              "cta", "canonical_url", "media", "claims", "disclosures",
              "hashtags", "schedule")
    return sha(canon({k: package.get(k) for k in fields}))


def build_variant(package: dict, surface: str, account_id: str,
                  modes: dict) -> dict:
    spec = SURFACES[surface]
    copy_src = package.get("short_copy") or package.get("body") or ""
    copy_text = copy_src
    if len(copy_src) > spec["char_limit"]:
        copy_text = copy_src[:spec["char_limit"] - 1].rstrip() + "…"
    media_in = package.get("media") or []
    if surface == "carousel":
        media = [{"asset_id": m["asset_id"], "card": i + 1,
                  "aspect_out": spec["aspect"]}
                 for i, m in enumerate(media_in)]
        order = [f"card:{m['asset_id']}" for m in media_in] \
            + ["caption", "link_via_profile"]
    else:
        media = [{"asset_id": m["asset_id"], "aspect_out": spec["aspect"]}
                 for m in media_in]
        order = ["media", "caption", "link_via_profile"] \
            if surface != "story" else ["media", "link_sticker", "caption"]
    disclosures_out = dict(package.get("disclosures") or {})
    if disclosures_out.get("ai_media"):
        disclosures_out["platform_ai_label"] = True
    variant = {
        "variant_id": f"{package['canonical_id']}::aperture_{surface}",
        "canonical_id": package["canonical_id"],
        "canonical_hash": content_hash_of(package),
        "adapter": "aperture", "surface": surface,
        "destination_account": account_id,
        "media": media, "copy_text": copy_text,
        "link": {"placement": spec["link_placement"],
                 "url": package.get("canonical_url"),
                 "clickable_in_caption": spec["links_clickable"]},
        "hashtags": list(package.get("hashtags") or []),
        "disclosures_out": disclosures_out,
        "order": order,
        "schedule": package.get("schedule"),
        "mode": modes.get("publishing", "PREP_PACK"),
        "safe_zones": spec["safe_zones"],
    }
    variant["diffs"] = compute_diffs(package, variant, spec)
    variant["variant_hash"] = variant_hash(variant)
    return variant


def compute_diffs(package: dict, variant: dict, spec: dict):
    diffs = []
    for m_in, m_out in zip(package.get("media") or [], variant["media"]):
        if m_out["aspect_out"] != m_in.get("aspect"):
            diffs.append({"category": "MEDIA_CROP",
                          "field": f"media:{m_in['asset_id']}",
                          "from": m_in.get("aspect"),
                          "to": m_out["aspect_out"], "substantive": False})
    canon_copy = package.get("short_copy") or package.get("body") or ""
    if variant["copy_text"] != canon_copy:
        diffs.append({"category": "TEXT_REWRITE", "field": "copy_text",
                      "from": canon_copy, "to": variant["copy_text"],
                      "substantive": False})
    diffs.append({"category": "LINK_PLACEMENT", "field": "link",
                  "from": {"placement": "canonical_url",
                           "url": package.get("canonical_url")},
                  "to": variant["link"], "substantive": False,
                  "note": "Instagram captions carry no clickable link; "
                          "the working path is the profile link"
                          + (" / Story link sticker." if variant["surface"] == "story"
                             else ". A raw URL in caption copy is not "
                                  "a conversion path (SS9).")})
    if variant["surface"] == "carousel":
        diffs.append({"category": "ORDER", "field": "order",
                      "from": ["media", "caption"],
                      "to": variant["order"], "substantive": False,
                      "note": "Carousel order is narrative order; the "
                              "first card carries the hook."})
    if variant["disclosures_out"] != (package.get("disclosures") or {}):
        diffs.append({"category": "DISCLOSURE", "field": "disclosures",
                      "from": package.get("disclosures") or {},
                      "to": variant["disclosures_out"],
                      "substantive": False,
                      "note": "Platform AI-media label carried on the "
                              "variant, not as a postscript."})
    return diffs


def t_variant_build(state, args):
    package = args["package"]
    surface = str(args.get("surface", "feed"))
    if surface not in SURFACES:
        raise ToolError(f"unknown surface {surface!r}; "
                        f"surfaces: {sorted(SURFACES)}")
    if not package.get("canonical_id"):
        raise ToolError("package carries no canonical_id — Aperture "
                        "builds variants of canonical packages only")
    modes = effective_modes(state)
    variant = build_variant(package, surface,
                            str(args.get("account_id", "")), modes)
    state["variants"][variant["variant_id"]] = variant
    r = emit_receipt(state, "variant_build",
                     {"variant_id": variant["variant_id"],
                      "variant_hash": variant["variant_hash"],
                      "mode": variant["mode"]})
    return {"variant": variant, "receipt_seq": r["seq"],
            "note": "Formalization only: no post was created. "
                    "Execution, if approved, runs through the house's "
                    "existing sanctioned Instagram route — referenced, "
                    "not duplicated (SS18)."}


def t_preview_pack(state, args):
    vid = str(args["variant_id"])
    v = state["variants"].get(vid)
    if not v:
        raise ToolError(f"unknown variant_id: {vid} — build it first")
    preview_lines = [
        f"APERTURE PREVIEW — {v['surface']} for @{v['destination_account']}",
        f"geometry: {v['media'][0]['aspect_out'] if v['media'] else 'n/a'}"
        f" | mode: {v['mode']} | variant hash: {v['variant_hash'][:16]}…",
        f"link path: {v['link']['placement']} -> {v['link']['url']}"
        f" (clickable in caption: {v['link']['clickable_in_caption']})",
        f"safe zones: {v['safe_zones']}",
        "caption:", v["copy_text"],
        "hashtags: " + " ".join(v["hashtags"]),
        "disclosures: " + json.dumps(v["disclosures_out"], sort_keys=True),
        "order: " + " -> ".join(v["order"]),
    ]
    return {"variant_id": vid, "variant": v,
            "native_preview": "\n".join(preview_lines),
            "diffs": v["diffs"],
            "approval_binds": {"canonical_hash": v["canonical_hash"],
                               "variant_hash": v["variant_hash"]},
            "note": "This pack is the review artifact. Approval binds "
                    "these exact hashes; any change returns the variant "
                    "to review (SS4)."}


def t_receipt_list(state, args):
    return {"receipts": state["receipts"],
            "count": len(state["receipts"]),
            "chain_valid": verify_receipt_chain(state["receipts"])}


TOOLS = {
    "capability_probe": (t_capability_probe, "Return Aperture's capability matrix from the STATIC declaration fixture (dated, [verify]-flagged): per-capability modes for an eligible professional Instagram account per spec SS9. NO live Graph API call is made in v0.1. Pass simulate_probe_failure=true to exercise the family downgrade rule: write modes collapse to prep, own-engagement to COMMUNITY_PREP.",
                         {"simulate_probe_failure": {"type": "boolean"}}, []),
    "variant_build": (t_variant_build, "Build one native Instagram variant (feed 4:5 | carousel narrative order | reel 9:16 | story 9:16) from a canonical content package: geometry, caption, the working link path (profile link / Story sticker — caption links are not clickable), platform AI-media label, classified diff vs canonical, and the variant's hash. Formalization only — nothing is posted.",
                      {"package": {"type": "object"}, "surface": {"type": "string"}, "account_id": {"type": "string"}}, ["package"]),
    "preview_pack": (t_preview_pack, "The exact native preview for a built variant — rendered geometry/caption/link path/safe zones — plus its diffs and the hashes an approval would bind.",
                     {"variant_id": {"type": "string"}}, ["variant_id"]),
    "receipt_list": (t_receipt_list, "The append-only, hash-chained receipt ledger, with chain verification.",
                     {}, []),
}


def tool_list():
    return [{"name": name, "description": desc,
             "inputSchema": {"type": "object", "properties": props, "required": req}}
            for name, (_, desc, props, req) in TOOLS.items()]


def handle(req: dict):
    method, rid = req.get("method", ""), req.get("id")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": rid, "result": {
            "protocolVersion": req.get("params", {}).get("protocolVersion", "2025-03-26"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "eclipse-aperture", "version": "0.1.0"}}}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": rid, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": tool_list()}}
    if method == "tools/call":
        name = req["params"]["name"]
        args = req["params"].get("arguments", {})
        if name not in TOOLS:
            return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32602, "message": f"unknown tool {name}"}}
        state = load_state()
        try:
            out = TOOLS[name][0](state, args)
            save_state(state)
            return {"jsonrpc": "2.0", "id": rid, "result": {
                "content": [{"type": "text", "text": json.dumps(out, indent=1)}]}}
        except ToolError as e:
            save_state(state)
            return {"jsonrpc": "2.0", "id": rid, "result": {
                "content": [{"type": "text", "text": json.dumps({"error": str(e)})}], "isError": True}}
    if rid is not None:
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"method not found: {method}"}}
    return None  # notification


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            resp = handle(json.loads(line))
        except Exception as e:  # never crash the transport
            resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}}
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
