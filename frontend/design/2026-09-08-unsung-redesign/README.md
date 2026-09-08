# Unsung.fm redesign — the mockup, as exported 2026-09-08

**Source:** the owner's Claude Design project *"Unsung.fm redesign kickoff"*
(`claude.ai/design/p/57b872ea-015e-472d-8ee8-06f1fb76a19d`), file `Unsung.fm.dc.html`,
read through the Design MCP on 2026-09-08. Direction **1a "Signal, with docked artist
detail"** is the one he selected; the project's own sync note says so.

**What governs.** The mockup is the *visual* source. Scope — which of its elements are built,
deferred or dropped, and every decision the owner took over it — is
`docs/superpowers/specs/2026-09-08-unsung-redesign-scope.md`. Where the mockup and the spec
disagree, **the spec governs**: the mockup draws four things the spec drops (the reach pill,
the genre chips, the "Why this stop" prose, "Save track") and one it defers (the top nav and
the pages behind it).

**What the mockup does not know.** Its "current build" artboard was recreated from source on
2026-09-04 at 02:00, before `LUX-1`–`LUX-4` merged. It shows "Steer away" and the reroute
tray (both gone) and has no home for the skipped-artists panel (`LUX-2`), "Try another track"
(`LUX-3`) or the Apple Music link (`LUX-4`). The spec places those.

## Files

| file | what |
|---|---|
| `Unsung.fm.dc.html` | the two artboards (landing, journey), desktop and mobile, verbatim |
| `support.js` | the Design Canvas runtime the file needs to render; vendored, generated, not ours |
| `assets/` | **empty — see below** |

**The PNG assets did not survive the export.** `assets/unsung-mark.png` is a 1152×1152 PNG
the MCP returns truncated at 256 KB, and `assets/unsung-logo.png` likewise. **The owner
exports both from the Design project by hand** and drops them here (and the mark, resized,
where the plan's branding task names). Until then the mockup renders with two broken image
boxes and nothing else missing.

Same convention as `2026-07-28-mockup/` and `2026-08-07-bypass-tray/`. Open the `.dc.html`
in a browser from this directory; it loads Google Fonts from the network, which the app itself
does not (the app self-hosts both faces through `@fontsource-variable`).
