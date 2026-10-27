# eclipse-aperture

**What this is:** the MCP server for **Eclipse Aperture** — the
Instagram adapter of Cyan Eclipse Technologies' Eclipse social
adapter family, formalized. One approved package becomes native Feed,
Carousel, Story, and Reel variants for a professional account, with
publishing and analytics only through Meta's sanctioned Graph API
surface.

**What this is not:** v0.1 is a formalization, **not a second Instagram
pipe**. It posts nothing and makes no live Graph API calls. The
house's existing sanctioned connector route is referenced here, never
duplicated — no token path, session handling, or credential material
exists in this server.

## Run it

```console
$ pip install eclipse-aperture
$ eclipse-aperture           # MCP over stdio, Python stdlib only
```

MCP client config:

```json
{ "mcpServers": { "eclipse-aperture": { "command": "uvx", "args": ["eclipse-aperture"] } } }
```

## Tools (4)

`capability_probe` · `variant_build` · `preview_pack` · `receipt_list`

- `capability_probe` returns the capability matrix from a **static
  declaration fixture** (dated, `[verify]`-flagged). A simulated probe
  failure downgrades the declared modes exactly as the family core
  prescribes — write modes collapse to prep, never to a workaround.
- `variant_build` builds Feed (4:5), Carousel (narrative order), Reel
  (9:16), and Story (9:16) variants, each hash-bound with classified
  diffs vs canonical and the working link path (profile link / Story
  sticker — caption links are not clickable and are never the
  conversion path).
- `preview_pack` is the exact native preview the owner approves.

## Honest scope

- **Formalization only (phase S0).** Approval here binds hashes;
  execution happens only through the house's existing sanctioned
  route, outside this product.
- State persists in `data/state.json` beside the server (override with
  `ECLIPSE_APERTURE_STATE`); the capability declaration ships in the
  wheel at `fixtures/capability.json`.
- Certified (local) by the Eclipse Test Bench at v0.1.0; the listing
  status in the Eclipse Bazaar catalog is in-development.

Powered by Cyan Eclipse Technologies LLC (cetech.ai) — a Veteran-Owned
Small Business. MIT licensed. Not affiliated with Meta or Instagram;
platform names describe the adapter surface only.
