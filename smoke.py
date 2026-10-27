#!/usr/bin/env python3
# Eclipse Aperture MCP
# Copyright © 2026 Cyan Eclipse Technologies LLC · cetech.ai
# Smoke: drive server.py over real stdio with a temp state file.

"""Smoke: drive server.py over real stdio with a temp state file.
Probes the static capability declaration, builds a Reel variant from
the core's sample package, renders its preview pack. NO live calls."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent
CORE_FIX = ROOT / "fixtures" / "sample_content.json"


def call(proc, rid, name, args):
    proc.stdin.write(json.dumps({"jsonrpc": "2.0", "id": rid,
                                 "method": "tools/call",
                                 "params": {"name": name,
                                            "arguments": args}}) + "\n")
    proc.stdin.flush()
    resp = json.loads(proc.stdout.readline())
    return json.loads(resp["result"]["content"][0]["text"])


def main():
    with tempfile.TemporaryDirectory() as td:
        env = {"ECLIPSE_APERTURE_STATE": str(Path(td) / "state.json"),
               "PATH": "/usr/bin:/bin:/usr/local/bin"}
        proc = subprocess.Popen([sys.executable, str(ROOT / "server.py")],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                text=True, env=env)
        try:
            proc.stdin.write(json.dumps(
                {"jsonrpc": "2.0", "id": 0, "method": "initialize",
                 "params": {"protocolVersion": "2025-03-26"}}) + "\n")
            proc.stdin.flush()
            init = json.loads(proc.stdout.readline())
            print("server:", init["result"]["serverInfo"])
            probe = call(proc, 1, "capability_probe", {})
            print("probe:", probe["probe_type"], "| status:",
                  probe["status"], "| publishing:",
                  probe["effective_modes"]["publishing"],
                  "| community:", probe["effective_modes"]
                  ["community_engagement"])
            package = json.loads(CORE_FIX.read_text())
            out = call(proc, 2, "variant_build",
                       {"package": package, "surface": "reel",
                        "account_id": "acevvswhite"})
            vid = out["variant"]["variant_id"]
            print("variant:", vid, "| hash:",
                  out["variant"]["variant_hash"][:16], "| diffs:",
                  [d["category"] for d in out["variant"]["diffs"]])
            pack = call(proc, 3, "preview_pack", {"variant_id": vid})
            print("--- native preview ---")
            print(pack["native_preview"])
            rec = call(proc, 4, "receipt_list", {})
            print("receipts:", rec["count"], "chain valid:",
                  rec["chain_valid"])
        finally:
            proc.stdin.close()
            proc.wait(timeout=10)


if __name__ == "__main__":
    main()

# Eclipse Aperture MCP · © 2026 Cyan Eclipse Technologies LLC · cetech.ai
