#!/usr/bin/env python3
# Eclipse Aperture MCP
# Copyright © 2026 Cyan Eclipse Technologies LLC · cetech.ai
# Eclipse Aperture v0.1 (S0 formalization) — unit tests.

"""Eclipse Aperture v0.1 (S0 formalization) — unit tests.
Run: python3 -m unittest discover tests"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import server as A  # noqa: E402

ROOT = Path(__file__).parent.parent
CORE_FIX = ROOT / "fixtures" / "sample_content.json"


def package():
    return json.loads(CORE_FIX.read_text())


class TestCapabilityDeclaration(unittest.TestCase):
    def test_declaration_modes_match_spec_chapter(self):
        st = A.empty_state()
        out = A.t_capability_probe(st, {})
        self.assertEqual(out["probe_type"], "static_declaration")
        self.assertFalse(out["live_calls_made"])
        eff = out["effective_modes"]
        self.assertEqual(eff["publishing"], "PUBLISH_API")
        self.assertEqual(eff["reads"], "READ_API")
        self.assertEqual(eff["own_engagement"], "OWN_ENGAGEMENT_API")
        # Community engagement is PREP for every chapter at launch (SS5.2)
        self.assertEqual(eff["community_engagement"], "COMMUNITY_PREP")
        self.assertFalse(out["downgraded"])

    def test_failed_probe_downgrades(self):
        st = A.empty_state()
        out = A.t_capability_probe(st, {"simulate_probe_failure": True})
        self.assertTrue(out["downgraded"])
        eff = out["effective_modes"]
        self.assertEqual(eff["publishing"], "PREP_PACK")
        self.assertEqual(eff["drafts"], "PREP_PACK")
        self.assertEqual(eff["own_engagement"], "COMMUNITY_PREP")
        self.assertEqual(eff["community_engagement"], "COMMUNITY_PREP")
        self.assertEqual(eff["reads"], "READ_API")
        # declared matrix is preserved alongside the downgrade
        self.assertEqual(out["declared_modes"]["publishing"],
                         "PUBLISH_API")

    def test_downgrade_flows_into_built_variant_mode(self):
        st = A.empty_state()
        A.t_capability_probe(st, {"simulate_probe_failure": True})
        out = A.t_variant_build(st, {"package": package(),
                                     "surface": "reel",
                                     "account_id": "acevvswhite"})
        self.assertEqual(out["variant"]["mode"], "PREP_PACK")


class TestVariants(unittest.TestCase):
    def test_reel_geometry_and_link_path(self):
        st = A.empty_state()
        out = A.t_variant_build(st, {"package": package(),
                                     "surface": "reel",
                                     "account_id": "acevvswhite"})
        v = out["variant"]
        self.assertEqual(v["media"][0]["aspect_out"], "9:16")
        self.assertEqual(v["link"]["placement"], "profile_link")
        self.assertFalse(v["link"]["clickable_in_caption"])
        cats = {d["category"] for d in v["diffs"]}
        self.assertIn("LINK_PLACEMENT", cats)

    def test_feed_crop_diff(self):
        st = A.empty_state()
        out = A.t_variant_build(st, {"package": package(),
                                     "surface": "feed",
                                     "account_id": "acevvswhite"})
        v = out["variant"]
        self.assertEqual(v["media"][0]["aspect_out"], "4:5")
        cats = {d["category"] for d in v["diffs"]}
        self.assertIn("MEDIA_CROP", cats)  # master is 9:16

    def test_carousel_order_is_narrative(self):
        st = A.empty_state()
        out = A.t_variant_build(st, {"package": package(),
                                     "surface": "carousel",
                                     "account_id": "acevvswhite"})
        v = out["variant"]
        self.assertEqual([m["card"] for m in v["media"]], [1, 2])
        self.assertTrue(v["order"][0].startswith("card:"))
        cats = {d["category"] for d in v["diffs"]}
        self.assertIn("ORDER", cats)

    def test_story_link_sticker_is_the_clickable_path(self):
        st = A.empty_state()
        out = A.t_variant_build(st, {"package": package(),
                                     "surface": "story",
                                     "account_id": "acevvswhite"})
        v = out["variant"]
        self.assertEqual(v["link"]["placement"], "story_link_sticker")
        self.assertTrue(v["link"]["clickable_in_caption"])

    def test_ai_label_carried_on_variant(self):
        st = A.empty_state()
        out = A.t_variant_build(st, {"package": package(),
                                     "surface": "feed",
                                     "account_id": "acevvswhite"})
        self.assertTrue(
            out["variant"]["disclosures_out"]["platform_ai_label"])
        cats = {d["category"] for d in out["variant"]["diffs"]}
        self.assertIn("DISCLOSURE", cats)

    def test_variant_hash_binds_content(self):
        st = A.empty_state()
        v1 = A.t_variant_build(st, {"package": package(),
                                    "surface": "feed",
                                    "account_id": "acevvswhite"})["variant"]
        changed = package()
        changed["short_copy"] = "Different copy entirely."
        v2 = A.t_variant_build(st, {"package": changed,
                                    "surface": "feed",
                                    "account_id": "acevvswhite"})["variant"]
        self.assertNotEqual(v1["variant_hash"], v2["variant_hash"])
        self.assertNotEqual(v1["canonical_hash"], v2["canonical_hash"])

    def test_preview_pack_renders_native_facts(self):
        st = A.empty_state()
        out = A.t_variant_build(st, {"package": package(),
                                     "surface": "reel",
                                     "account_id": "acevvswhite"})
        pack = A.t_preview_pack(st, {"variant_id":
                                     out["variant"]["variant_id"]})
        self.assertIn("9:16", pack["native_preview"])
        self.assertIn("profile_link", pack["native_preview"])
        self.assertEqual(pack["approval_binds"]["variant_hash"],
                         out["variant"]["variant_hash"])

    def test_receipts_chain(self):
        st = A.empty_state()
        A.t_capability_probe(st, {})
        A.t_variant_build(st, {"package": package(), "surface": "feed",
                               "account_id": "acevvswhite"})
        out = A.t_receipt_list(st, {})
        self.assertEqual(out["count"], 2)
        self.assertTrue(out["chain_valid"])


if __name__ == "__main__":
    unittest.main()

# Eclipse Aperture MCP · © 2026 Cyan Eclipse Technologies LLC · cetech.ai
