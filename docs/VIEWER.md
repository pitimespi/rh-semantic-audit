# RH Semantic Graph — interactive viewer

The [viewer](../viewer/index.html) displays **source-linked, provisional semantic theorem graphs** for the claimed RH formalization. It does not run Lean, use authentication, or change theorem/research submissions.

## Run locally

From a clone of this repository:

```bash
python3 -m http.server 8000
```

Visit `http://localhost:8000/viewer/` in a browser. The three RH-only views are:

1. **Actual central RH bridge (recommended):** [`rh_actual_bridge.json`](../examples/rh_actual_bridge.json). Maps the real `every_character_of_theta_integrals_local_matching` theorem, its seven supplied premises, its definite-side `HypsAlt` construction, and the Green/window to nonvanishing step. See [AUDIT-005](../audit/AUDIT-005-EXACT-THETA-BRIDGE.md).
2. **Headline theorem chain:** [`rh_critical_path.json`](../examples/rh_critical_path.json). Source-linked route from Galois/row witnesses to the final RH statement, now including the actual central theta theorem.
3. **Earlier analogous bridge (comparison only):** [`rh_analytic_bridge.json`](../examples/rh_analytic_bridge.json). A different theorem, `everyE₂`, with different analytic hypotheses. It is **not** established as a direct dependency of the headline route.

The **Open local JSON** option works without a local web server. It uses `FileReader` in the browser; the file is not uploaded. The example-loading buttons usually need `http://localhost` because modern browsers restrict `file://` fetches.

## Read the graph critically

Each node displays a source-pinned statement, currently recorded assumptions and a plain-language mathematical read-back. Each edge displays an evidence grade, a source citation, a proposed mathematical role and review status.

All edges in the current RH fixtures are **source references**, not independently extracted Lean kernel proof-term dependencies. No mathematical explanation is marked independently reviewed. If two theorem types appear analogous, the interface does not assume they are definitionally or mathematically equivalent.

This viewer uses a bounded SVG DAG layout, not a tool for hundreds of thousands of declarations. It avoids external JavaScript packages, trackers, third-party fonts and credentials. Imported prose is inserted as text rather than HTML. Run `python3 -m semantic_graph.cli validate examples/rh_actual_bridge.json` on new JSON before relying on its structural integrity.

## Source reproducibility

GitHub CI runs the Python graph validator, JavaScript syntax check and automated source-line verification against the immutable mirror commit. To run the RH source checks locally from the repository root:

```bash
python3 tools/rh_interface_check.py --fetch-pinned
python3 -m tools.rh_analytic_check --fetch-pinned --graph examples/rh_actual_bridge.json
```

These are **textual source correspondence checks**, not mathematical, elaboration, kernel or axiom audits.
