# Diagrams

This folder documents MikroTik MCP visually, using [draw.io](https://www.drawio.com/)
(diagrams.net) diagrams that live in the repository next to the code they
describe. Architecture decisions are easier to review as a picture than as
prose, and keeping the `.drawio` sources here means the diagrams version
together with the code: when a pull request changes how the server works, it
can change the drawing in the same commit.

## Current diagrams

| Diagram | What it shows |
|---|---|
| [`Inventory.drawio`](Inventory.drawio) | The multi-device inventory architecture (issue [#44](https://github.com/jeff-nasseri/mikrotik-mcp/issues/44)): the LLM calls MCP tools, each tool passes a device `title` to the connector, the Inventory resolves the title to that device's SSH client, and the command runs on the selected router. Tool D is `list_devices`, which lets the LLM discover the fleet. |

## Viewing and editing

GitHub does not render `.drawio` files inline, so open them with one of:

- **[app.diagrams.net](https://app.diagrams.net/)** — File → Open From → Device
  (no account needed), or open directly from GitHub via File → Open From → GitHub.
- **draw.io Desktop** — the [offline application](https://github.com/jgraph/drawio-desktop/releases).
- **VS Code** — the [Draw.io Integration extension](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio)
  edits `.drawio` files right in the editor.

## Adding a diagram

Incoming diagrams are welcome — the goal is for every non-trivial subsystem to
have a picture. A few conventions keep the folder useful:

1. **One topic per file**, named after the subsystem it describes
   (`Inventory.drawio`, `SafeMode.drawio`, …).
2. **Always commit the `.drawio` source.** It is XML, so it diffs and merges
   like any other text file. Do not commit only an exported image, because
   nobody can edit a PNG.
3. **Export a `.png` or `.svg` next to the source** (same basename) when a
   diagram should appear inline in other documentation — markdown can embed
   the export while the `.drawio` file stays the editable source of truth.
   In draw.io: File → Export as → PNG/SVG.
4. **Link the diagram from the docs page it illustrates**, and add a row to
   the table above so the folder stays discoverable.
5. **Update the drawing in the same pull request that changes the behaviour**
   it describes. A diagram that no longer matches the code is worse than no
   diagram at all.
