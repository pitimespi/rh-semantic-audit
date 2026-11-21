/* Semantic Proof Graph viewer — no external JS dependencies.
 * Loads examples relative to the repository, or an arbitrary local JSON
 * file selected by the user. No graph data or credentials are uploaded.
 */
"use strict";

(function () {
  const svgNS = "http://www.w3.org/2000/svg";
  const canvas = document.getElementById("canvas");
  const viewport = document.getElementById("viewport");
  const detail = document.getElementById("detail");
  const status = document.getElementById("status");

  let graph = null;
  let selectedId = null;
  const kinds = {
    source_reference: { color: "#526b76", dash: "" },
    import_candidate: { color: "#9baab3", dash: "8 5" },
    platform_decomposition: { color: "#b5703d", dash: "2 6" },
    kernel_dependency: { color: "#0b7b5d", dash: "" },
  };

  function div(parent, tag, text, cls) {
    const el = document.createElement(tag);
    if (text !== undefined && text !== null) el.textContent = String(text);
    if (cls) el.className = cls;
    parent.appendChild(el);
    return el;
  }

  function safeLink(parent, label, url) {
    if (typeof url !== "string" || !url.startsWith("https://github.com/")) return;
    const link = div(parent, "a", label);
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
  }

  function svgEl(name, attrs, parent) {
    const e = document.createElementNS(svgNS, name);
    Object.entries(attrs || {}).forEach(function (item) {
      e.setAttribute(item[0], String(item[1]));
    });
    if (parent) parent.appendChild(e);
    return e;
  }

  function truncate(s, n) {
    const text = String(s || "");
    return text.length > n ? text.slice(0, n - 1) + "…" : text;
  }

  function graphProblems(raw) {
    const errors = [];
    if (!raw || typeof raw !== "object" || raw.schema_version !== "semantic-proof-graph/v1") {
      errors.push("Not a semantic-proof-graph/v1 document");
      return errors;
    }
    if (!raw.project || !Array.isArray(raw.nodes) || !Array.isArray(raw.edges)) {
      errors.push("Missing project, nodes or edges");
      return errors;
    }
    if (raw.nodes.length > 500 || raw.edges.length > 2000) {
      errors.push("Graph too large for this preview (limit 500 nodes / 2000 edges)");
      return errors;
    }
    const ids = new Set();
    raw.nodes.forEach(function (n) {
      if (!n || typeof n.id !== "string" || typeof n.symbol !== "string" ||
          typeof n.title !== "string" || typeof n.statement !== "string" ||
          ids.has(n.id)) {
        errors.push("Invalid or duplicated node");
      } else {
        ids.add(n.id);
      }
    });
    raw.edges.forEach(function (e) {
      if (!e || !ids.has(e.from) || !ids.has(e.to) || !kinds[e.kind]) {
        errors.push("Invalid edge or evidence class");
      }
    });
    return errors;
  }

  function layout(g) {
    const incoming = new Map();
    const outgoing = new Map();
    const layer = new Map();
    g.nodes.forEach(function (n) {
      incoming.set(n.id, 0);
      outgoing.set(n.id, []);
      layer.set(n.id, 0);
    });
    g.edges.forEach(function (e) {
      incoming.set(e.to, incoming.get(e.to) + 1);
      outgoing.get(e.from).push(e.to);
    });
    const queue = g.nodes.filter(function (n) {
      return incoming.get(n.id) === 0;
    }).map(function (n) { return n.id; }).sort();
    let seen = 0;
    while (queue.length) {
      const id = queue.shift();
      seen += 1;
      outgoing.get(id).forEach(function (next) {
        layer.set(next, Math.max(layer.get(next), layer.get(id) + 1));
        incoming.set(next, incoming.get(next) - 1);
        if (incoming.get(next) === 0) {
          queue.push(next);
          queue.sort();
        }
      });
    }
    if (seen !== g.nodes.length) throw Error("A dependency cycle prevents DAG layout.");
    const columns = new Map();
    g.nodes.forEach(function (n) {
      const index = layer.get(n.id);
      if (!columns.has(index)) columns.set(index, []);
      columns.get(index).push(n);
    });
    columns.forEach(function (ns) { ns.sort(function (a, b) { return a.title.localeCompare(b.title); }); });
    const maxDepth = Math.max(0, ...columns.keys());
    const maxPerColumn = Math.max(1, ...Array.from(columns.values()).map(function (ns) { return ns.length; }));
    const width = Math.max(800, 64 + (maxDepth + 1) * 310);
    const height = Math.max(460, 80 + maxPerColumn * 136);
    const positions = new Map();
    columns.forEach(function (ns, index) {
      ns.forEach(function (n, i) {
        positions.set(n.id, { x: 38 + index * 310, y: 54 + i * 136 });
      });
    });
    return { positions: positions, width: width, height: height };
  }

  function paint() {
    canvas.replaceChildren();
    if (!graph) return;
    const bounds = layout(graph);
    canvas.setAttribute("width", bounds.width);
    canvas.setAttribute("height", bounds.height);
    canvas.setAttribute("viewBox", "0 0 " + bounds.width + " " + bounds.height);

    const defs = svgEl("defs", {}, canvas);
    const arrow = svgEl("marker", {
      id: "edge-arrow", markerWidth: 9, markerHeight: 9, refX: 7, refY: 4.5,
      orient: "auto", markerUnits: "strokeWidth",
    }, defs);
    svgEl("path", { d: "M 0 0 L 8 4.5 L 0 9 z", fill: "#81939d" }, arrow);

    graph.edges.forEach(function (e) {
      const from = bounds.positions.get(e.from);
      const to = bounds.positions.get(e.to);
      const color = kinds[e.kind];
      const sx = from.x + 250, sy = from.y + 40, tx = to.x, ty = to.y + 40;
      const delta = Math.max(36, (tx - sx) * 0.48);
      const path = "M " + sx + " " + sy + " C " + (sx + delta) + " " + sy +
                   ", " + (tx - delta) + " " + ty + ", " + (tx - 4) + " " + ty;
      const nearSelected = !selectedId || e.from === selectedId || e.to === selectedId;
      svgEl("path", {
        d: path, stroke: color.color, "stroke-width": nearSelected ? 2.3 : 1.1,
        "stroke-dasharray": color.dash, fill: "none",
        opacity: nearSelected ? 0.92 : 0.18,
        "marker-end": "url(#edge-arrow)",
      }, canvas);
    });

    graph.nodes.forEach(function (n) {
      const point = bounds.positions.get(n.id);
      const current = selectedId === n.id;
      const neighboring = !selectedId || current || graph.edges.some(function (e) {
        return (e.from === selectedId && e.to === n.id) ||
               (e.to === selectedId && e.from === n.id);
      });
      const group = svgEl("g", {
        transform: "translate(" + point.x + " " + point.y + ")",
        role: "button", tabindex: 0, "aria-label": "Inspect " + n.symbol,
        opacity: neighboring ? 1 : 0.38, style: "cursor:pointer",
      }, canvas);
      svgEl("rect", {
        x: 0, y: 0, rx: 12, width: 250, height: 84,
        fill: current ? "#e5f7f5" : "#fff",
        stroke: current ? "#0b6f77" : "#bdced4",
        "stroke-width": current ? 2.6 : 1.2,
      }, group);
      let title = svgEl("text", {
        x: 14, y: 28, "font-size": 13.5, "font-weight": 700, fill: "#18252b",
      }, group);
      title.textContent = truncate(n.title, 31);
      let symbol = svgEl("text", {
        x: 14, y: 54, "font-size": 10.8, fill: "#536b75",
        "font-family": "ui-monospace, monospace",
      }, group);
      symbol.textContent = truncate(n.symbol, 32);
      svgEl("circle", {
        cx: 234, cy: 68, r: 4,
        fill: current ? "#0b6f77" : "#adbbc0",
      }, group);
      const onSelect = function () { select(n.id); };
      group.addEventListener("click", onSelect);
      group.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          onSelect();
        }
      });
    });
  }

  function edgeDetail(parent, e, heading, peer) {
    const section = div(parent, "div", undefined, "edge");
    const head = div(section, "div", undefined, "edge-head");
    div(head, "span", peer.title, "role");
    div(head, "span", e.kind.replaceAll("_", " "), "badge");
    div(head, "span", e.semantic && e.semantic.review_status || "not reviewed", "badge");
    div(section, "p", heading + ": " +
      (e.semantic && e.semantic.role || "No semantic role supplied"), "note");
    div(section, "p", e.semantic && e.semantic.explanation ||
      "No explanation has been supplied; this is not a mathematical review.");
    if (e.evidence && e.evidence.source) {
      safeLink(section, "Source evidence", e.evidence.source.url);
    }
    if (e.evidence && e.evidence.api && e.evidence.api.submission_id) {
      div(section, "p", "Platform sketch submission: " +
        e.evidence.api.submission_id, "symbol");
    }
    return section;
  }

  function select(id) {
    if (!graph) return;
    const node = graph.nodes.find(function (n) { return n.id === id; });
    if (!node) return;
    selectedId = id;
    paint();
    detail.replaceChildren();
    div(detail, "div", "Selected theorem", "kicker");
    div(detail, "h2", node.title);
    div(detail, "div", node.symbol, "symbol");
    div(detail, "h3", "Mathematical statement (human read-back)");
    div(detail, "div", node.statement, "statement");
    if (node.source) {
      const line = div(detail, "p", undefined, "note");
      safeLink(line, "Pinned source declaration", node.source.url);
    }
    if (node.proposal_record) {
      div(detail, "h3", "Local proposal provenance");
      div(detail, "p", "Proposal item (not theorem ID): " +
        node.proposal_record.proposal_item_id, "symbol");
      if (node.proposal_record.repository_reported_submission_status) {
        div(detail, "p", "Repository-reported status: " +
          node.proposal_record.repository_reported_submission_status, "note");
      }
    }
    if (node.theorem_record) {
      div(detail, "h3", "Platform theorem snapshot");
      div(detail, "p", "Theorem ID: " + node.theorem_record.theorem_id, "symbol");
      div(detail, "p", "Cached status: " +
        node.theorem_record.status_as_reported_by_api, "note");
    }
    div(detail, "h3", "Explicit assumptions");
    if (!node.assumptions || !node.assumptions.length) {
      div(detail, "p", "No explicit assumptions recorded in this fixture; implicit hypotheses are not ruled out.", "note");
    } else {
      const ul = div(detail, "ul");
      node.assumptions.forEach(function (a) {
        div(ul, "li", a.name + " — " + a.meaning);
      });
    }
    const index = new Map(graph.nodes.map(function (n) { return [n.id, n]; }));
    const premises = graph.edges.filter(function (e) { return e.to === id; });
    div(detail, "h3", "Premises (" + premises.length + ")");
    if (!premises.length) div(detail, "p", "No incoming dependency edges represented.", "note");
    premises.forEach(function (e) { edgeDetail(detail, e, "Why this appears", index.get(e.from)); });
    const dependents = graph.edges.filter(function (e) { return e.from === id; });
    div(detail, "h3", "Used by (" + dependents.length + ")");
    if (!dependents.length) div(detail, "p", "No outgoing dependencies represented.", "note");
    dependents.forEach(function (e) { edgeDetail(detail, e, "Relationship", index.get(e.to)); });
  }

  function showGraph(raw, label) {
    const problems = graphProblems(raw);
    if (problems.length) throw Error(problems.slice(0, 4).join("; "));
    const oldGraph = graph;
    graph = raw;
    try {
      layout(graph);
    } catch (err) {
      graph = oldGraph;
      throw err;
    }
    selectedId = null;
    status.textContent = label + " · " + graph.nodes.length + " nodes, " +
      graph.edges.length + " edges · provisional explanations";
    status.classList.remove("error");
    paint();
    if (graph.nodes.length) select(graph.nodes[graph.nodes.length - 1].id);
    viewport.scrollLeft = 0;
    viewport.scrollTop = 0;
  }

  async function loadExample(file, label) {
    try {
      const response = await fetch("../examples/" + file, { cache: "no-store" });
      if (!response.ok) throw Error("Example could not be loaded (" + response.status + ")");
      const raw = await response.json();
      showGraph(raw, label);
    } catch (err) {
      status.textContent = "Couldn't open example here. Run 'python3 -m http.server 8000' " +
        "from the repository root, or use Open local JSON: " + err.message;
      status.classList.add("error");
    }
  }

  document.getElementById("bitcoin").addEventListener("click", function () {
    loadExample("bitcoin_supply_proposal_linked.json", "Prove2me Bitcoin supply");
  });
  document.getElementById("rh").addEventListener("click", function () {
    loadExample("rh_critical_path.json", "Alpöge RH source chain");
  });
  document.getElementById("upload").addEventListener("change", function (event) {
    const file = event.target.files && event.target.files[0];
    if (!file) return;
    if (file.size > 5_000_000) {
      status.textContent = "File too large for preview (5 MB max).";
      status.classList.add("error");
      return;
    }
    const reader = new FileReader();
    reader.onload = function () {
      try {
        showGraph(JSON.parse(reader.result), file.name);
      } catch (err) {
        status.textContent = "Cannot render graph: " + err.message;
        status.classList.add("error");
      }
    };
    reader.onerror = function () {
      status.textContent = "Could not read the local file.";
      status.classList.add("error");
    };
    reader.readAsText(file);
  });
}());
