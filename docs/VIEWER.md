# Interactive semantic proof graph viewer (read-only)

The [viewer](../viewer/index.html) is a dependency-free browser interface for the versioned JSON graph files in this repository. It is intentionally **not** part of the Lean proof system or the Prove2me platform.

## Running locally

From the root of a local clone of this repository, run:

\`\`\`sh
python3 -m http.server 8000
\`\`\`

Open \`http://localhost:8000/viewer/\` in a modern browser. Choose **Explore RH theorem chain**. The pages and example JSON load from your own local development server.

Alternatively, you can open \`viewer/index.html\` directly from your computer and choose **Open local JSON**. Browser security typically blocks the example-fetch buttons on \`file://\` URLs; the file-input option still works.

## Features

- Theorems are nodes, with arrows from *premises → conclusions*.
- Source references, import candidates, platform decomposition children, and kernel-level dependencies are visually distinguished.
- Selecting a node displays a human-readable statement, its source, assumptions, local proposal records or cached platform theorem ID, incoming prerequisites, downstream uses, explanatory prose, and review status.
- Every source link is pinned to a Git commit in the JSON fixture.
- The file uploader uses the browser's local \`FileReader\`. It does not transmit your graph data to an external service.
- No cookies, API access tokens, third-party JavaScript libraries, external fonts or trackers are used.
- The viewer escapes imported text via DOM \`textContent\` and only makes explicit source links to HTTPS GitHub URLs.
- The output remains read-only: the viewer does not edit source graphs or change a theorem's review status.

**Limitations:** The SVG layout is designed for curated graphs with at most 500 nodes and 2,000 edges, not a 17-million-line proof. It does not validate Lean syntax, prove theorem statements, inspect \`.olean\` files, resolve implicit elaboration dependencies, or fetch authenticated Prove2me data. Run the Python validator first on any third-party JSON input; the viewer performs only lightweight structural checks.

## Inputs and provenance

Use the active [RH source-level theorem path](../examples/rh_critical_path.json). Historical non-RH engineering fixtures are retained but no longer shown as default choices.

The Bitcoin proof has three **direct source-reference edges** supported by explicit theorem uses in the pinned solutions. Its two remaining edges are still only imported-theorem candidates. All explanatory relationships are in \`draft\` review status. See [BITCOIN-001](../audit/BITCOIN-001-SUPPLY.md) for a mathematical walkthrough.

The viewer never uses API credentials. The present research scope is only the purported RH formalization; no Prove2me platform submission has been made.

## Future viewer additions

- Filter by proof-relevant edge evidence (not all imports).
- Highlight which assumptions of one theorem are discharged by a particular premise.
- Integrate true kernel-exported dependency certificates as a separate evidence layer.
- Provide an independent review workflow and compare two separate read-backs.

No community engagement has been initiated.
