(() => {
  "use strict";

  const dataElement = document.getElementById("ecosystem-data");
  const map = document.getElementById("ecosystem-map");
  const edgeLayer = document.getElementById("ecosystem-connections");
  if (!dataElement || !map || !edgeLayer) return;

  const catalog = JSON.parse(dataElement.textContent);
  const tools = new Map(catalog.tools.map((tool) => [tool.id, tool]));
  const stages = new Map(catalog.stages.map((stage) => [stage.id, stage]));
  const groups = new Map(catalog.groups.map((group) => [group.id, group]));
  const statuses = new Map(catalog.statuses.map((status) => [status.id, status]));
  const relationshipTypes = new Map(
    catalog.relationship_types.map((type) => [type.id, type]),
  );
  const nodes = new Map(
    [...map.querySelectorAll(".ecosystem-node")].map((node) => [
      node.dataset.toolId,
      node,
    ]),
  );

  const controls = {
    search: document.getElementById("ecosystem-search"),
    stage: document.getElementById("ecosystem-stage-filter"),
    group: document.getElementById("ecosystem-group-filter"),
    status: document.getElementById("ecosystem-status-filter"),
    reset: document.getElementById("ecosystem-reset"),
    count: document.getElementById("ecosystem-result-count"),
  };
  const detail = {
    panel: document.getElementById("ecosystem-detail"),
    backdrop: document.getElementById("ecosystem-detail-backdrop"),
    close: document.getElementById("ecosystem-detail-close"),
    name: document.getElementById("ecosystem-detail-name"),
    status: document.getElementById("ecosystem-detail-status"),
    summary: document.getElementById("ecosystem-detail-summary"),
    description: document.getElementById("ecosystem-detail-description"),
    stage: document.getElementById("ecosystem-detail-stage"),
    group: document.getElementById("ecosystem-detail-group"),
    tags: document.getElementById("ecosystem-detail-tags"),
    links: document.getElementById("ecosystem-detail-links"),
    relationList: document.getElementById("ecosystem-detail-relation-list"),
    copy: document.getElementById("ecosystem-copy-link"),
  };

  const state = {
    selected: null,
    transient: null,
    previousFocus: null,
    drawFrame: null,
  };

  const linkLabels = {
    source: "Source",
    docs: "Documentation",
    package: "Package",
    website: "Website",
  };

  function isCurrentStatus(status) {
    return status !== "legacy";
  }

  function matchesFilters(node) {
    const query = controls.search.value.trim().toLowerCase();
    const statusFilter = controls.status.value;
    const matchesQuery = !query || node.dataset.search.includes(query);
    const matchesStage =
      controls.stage.value === "all" ||
      node.dataset.stage === controls.stage.value;
    const matchesGroup =
      controls.group.value === "all" ||
      node.dataset.group === controls.group.value;
    const matchesStatus =
      statusFilter === "all" ||
      (statusFilter === "current" && isCurrentStatus(node.dataset.status)) ||
      node.dataset.status === statusFilter;
    return matchesQuery && matchesStage && matchesGroup && matchesStatus;
  }

  function applyFilters() {
    let visibleCount = 0;
    nodes.forEach((node) => {
      const visible = matchesFilters(node);
      node.hidden = !visible;
      if (visible) visibleCount += 1;
    });

    map.querySelectorAll(".ecosystem-cell").forEach((cell) => {
      const hasVisibleNode = [...cell.querySelectorAll(".ecosystem-node")].some(
        (node) => !node.hidden,
      );
      cell.classList.toggle("is-empty", !hasVisibleNode);
    });
    catalog.groups.forEach((group) => {
      const hasVisibleNode = [...nodes.values()].some(
        (node) => node.dataset.group === group.id && !node.hidden,
      );
      const heading = map.querySelector(`[data-group-heading="${group.id}"]`);
      if (heading) heading.hidden = !hasVisibleNode;
    });

    controls.count.textContent = `${visibleCount} of ${catalog.tools.length} projects shown`;
    if (state.selected && nodes.get(state.selected)?.hidden) closeDetail(false);
    scheduleDraw();
  }

  function edgePath(source, target, mapRect) {
    const sourceRect = source.getBoundingClientRect();
    const targetRect = target.getBoundingClientRect();
    const sourceCenter = {
      x: sourceRect.left + sourceRect.width / 2 - mapRect.left,
      y: sourceRect.top + sourceRect.height / 2 - mapRect.top,
    };
    const targetCenter = {
      x: targetRect.left + targetRect.width / 2 - mapRect.left,
      y: targetRect.top + targetRect.height / 2 - mapRect.top,
    };
    const horizontalDistance = Math.abs(targetCenter.x - sourceCenter.x);

    if (horizontalDistance > 90) {
      const movingRight = targetCenter.x > sourceCenter.x;
      const startX =
        (movingRight ? sourceRect.right : sourceRect.left) - mapRect.left;
      const endX =
        (movingRight ? targetRect.left : targetRect.right) - mapRect.left;
      const middleX = startX + (endX - startX) / 2;
      return `M ${startX} ${sourceCenter.y} C ${middleX} ${sourceCenter.y}, ${middleX} ${targetCenter.y}, ${endX} ${targetCenter.y}`;
    }

    const movingDown = targetCenter.y > sourceCenter.y;
    const startY =
      (movingDown ? sourceRect.bottom : sourceRect.top) - mapRect.top;
    const endY =
      (movingDown ? targetRect.top : targetRect.bottom) - mapRect.top;
    const middleY = startY + (endY - startY) / 2;
    return `M ${sourceCenter.x} ${startY} C ${sourceCenter.x} ${middleY}, ${targetCenter.x} ${middleY}, ${targetCenter.x} ${endY}`;
  }

  function drawConnections() {
    state.drawFrame = null;
    edgeLayer.querySelectorAll(".ecosystem-edge").forEach((path) => path.remove());
    if (window.matchMedia("(max-width: 980px)").matches) return;

    const width = map.scrollWidth;
    const height = map.scrollHeight;
    edgeLayer.setAttribute("viewBox", `0 0 ${width} ${height}`);
    edgeLayer.setAttribute("width", String(width));
    edgeLayer.setAttribute("height", String(height));
    edgeLayer.style.width = `${width}px`;
    edgeLayer.style.height = `${height}px`;
    const mapRect = map.getBoundingClientRect();

    catalog.relationships.forEach((relationship) => {
      const source = nodes.get(relationship.source);
      const target = nodes.get(relationship.target);
      if (!source || !target || source.hidden || target.hidden) return;

      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.classList.add("ecosystem-edge");
      path.dataset.source = relationship.source;
      path.dataset.target = relationship.target;
      path.dataset.type = relationship.type;
      path.setAttribute("d", edgePath(source, target, mapRect));
      path.setAttribute("marker-end", "url(#ecosystem-arrow)");
      const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
      title.textContent = relationship.summary;
      path.appendChild(title);
      edgeLayer.appendChild(path);
    });
    applyHighlight(state.transient || state.selected);
  }

  function scheduleDraw() {
    if (state.drawFrame) cancelAnimationFrame(state.drawFrame);
    state.drawFrame = requestAnimationFrame(drawConnections);
  }

  function applyHighlight(toolId) {
    const relatedIds = new Set();
    if (toolId) {
      catalog.relationships.forEach((relationship) => {
        if (relationship.source === toolId) relatedIds.add(relationship.target);
        if (relationship.target === toolId) relatedIds.add(relationship.source);
      });
    }

    map.classList.toggle("has-focus", Boolean(toolId));
    nodes.forEach((node, nodeId) => {
      node.classList.toggle("is-focus", nodeId === toolId);
      node.classList.toggle("is-related", relatedIds.has(nodeId));
      node.classList.toggle("is-selected", nodeId === state.selected);
      node.setAttribute("aria-pressed", String(nodeId === state.selected));
    });
    edgeLayer.querySelectorAll(".ecosystem-edge").forEach((edge) => {
      edge.classList.toggle(
        "is-active",
        edge.dataset.source === toolId || edge.dataset.target === toolId,
      );
    });
  }

  function relatedRelationships(toolId) {
    return catalog.relationships.filter(
      (relationship) =>
        relationship.source === toolId || relationship.target === toolId,
    );
  }

  function relationButton(relationship, selectedId) {
    const otherId =
      relationship.source === selectedId
        ? relationship.target
        : relationship.source;
    const otherTool = tools.get(otherId);
    const type = relationshipTypes.get(relationship.type);
    const direction =
      relationship.source === selectedId ? "Outgoing" : "Incoming";
    const button = document.createElement("button");
    button.type = "button";
    button.className = "ecosystem-related-button";
    button.dataset.relationshipType = relationship.type;
    button.innerHTML = `<small>${direction} · ${type.label}</small><strong></strong><span></span>`;
    button.querySelector("strong").textContent = otherTool.name;
    button.querySelector("span").textContent = relationship.summary;
    button.addEventListener("click", () => selectTool(otherId, true, false));
    return button;
  }

  function populateDetail(tool) {
    detail.name.textContent = tool.name;
    detail.status.textContent = statuses.get(tool.status).label;
    detail.summary.textContent = tool.summary;
    detail.description.textContent = tool.description;
    detail.stage.textContent = stages.get(tool.stage).label;
    detail.group.textContent = groups.get(tool.group).label;

    detail.tags.replaceChildren(
      ...tool.tags.map((tag) => {
        const item = document.createElement("span");
        item.textContent = tag;
        return item;
      }),
    );
    detail.links.replaceChildren(
      ...Object.entries(tool.links).map(([kind, url]) => {
        const link = document.createElement("a");
        link.href = url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = `${linkLabels[kind] || kind} ↗`;
        return link;
      }),
    );

    const relationships = relatedRelationships(tool.id);
    if (relationships.length) {
      detail.relationList.replaceChildren(
        ...relationships.map((relationship) =>
          relationButton(relationship, tool.id),
        ),
      );
    } else {
      const empty = document.createElement("p");
      empty.className = "ecosystem-no-relations";
      empty.textContent = "No direct relationships are recorded yet.";
      detail.relationList.replaceChildren(empty);
    }
  }

  function setPageInert(inert) {
    document
      .querySelectorAll("body > header, body > main, body > footer")
      .forEach((element) => {
        element.inert = inert;
      });
  }

  function selectTool(toolId, updateHash = true, moveFocus = true) {
    const tool = tools.get(toolId);
    const node = nodes.get(toolId);
    if (!tool || !node) return;

    if (node.hidden) {
      controls.status.value = "all";
      applyFilters();
    }
    if (detail.panel.hidden) state.previousFocus = document.activeElement;
    state.selected = toolId;
    state.transient = null;
    populateDetail(tool);
    detail.panel.hidden = false;
    detail.backdrop.hidden = false;
    document.body.classList.add("detail-open");
    setPageInert(true);
    applyHighlight(toolId);
    if (updateHash) history.replaceState(null, "", `#${encodeURIComponent(toolId)}`);
    if (moveFocus) detail.close.focus();
  }

  function closeDetail(updateHash = true) {
    if (!state.selected && detail.panel.hidden) return;
    const selectedNode = state.selected ? nodes.get(state.selected) : null;
    state.selected = null;
    state.transient = null;
    detail.panel.hidden = true;
    detail.backdrop.hidden = true;
    document.body.classList.remove("detail-open");
    setPageInert(false);
    applyHighlight(null);
    if (updateHash) history.replaceState(null, "", window.location.pathname + window.location.search);

    const focusTarget =
      selectedNode && !selectedNode.hidden
        ? selectedNode
        : state.previousFocus instanceof HTMLElement && !state.previousFocus.hidden
          ? state.previousFocus
          : null;
    state.previousFocus = null;
    focusTarget?.focus();
  }

  function copySelectedLink() {
    if (!state.selected) return;
    const url = `${window.location.origin}${window.location.pathname}#${encodeURIComponent(state.selected)}`;
    const original = detail.copy.textContent;
    const confirm = () => {
      detail.copy.textContent = "Copied";
      window.setTimeout(() => {
        detail.copy.textContent = original;
      }, 1400);
    };
    if (navigator.clipboard?.writeText) {
      navigator.clipboard.writeText(url).then(confirm).catch(() => {});
      return;
    }
    const textarea = document.createElement("textarea");
    textarea.value = url;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    textarea.remove();
    confirm();
  }

  function openHashSelection() {
    const toolId = decodeURIComponent(window.location.hash.slice(1));
    if (toolId && tools.has(toolId)) selectTool(toolId, false, true);
    else if (!toolId && state.selected) closeDetail(false);
  }

  nodes.forEach((node, toolId) => {
    node.addEventListener("click", () => selectTool(toolId));
    node.addEventListener("pointerenter", () => {
      state.transient = toolId;
      applyHighlight(toolId);
    });
    node.addEventListener("pointerleave", () => {
      state.transient = null;
      applyHighlight(state.selected);
    });
    node.addEventListener("focus", () => {
      state.transient = toolId;
      applyHighlight(toolId);
    });
    node.addEventListener("blur", () => {
      state.transient = null;
      applyHighlight(state.selected);
    });
  });

  controls.search.addEventListener("input", applyFilters);
  [controls.stage, controls.group, controls.status].forEach((control) =>
    control.addEventListener("change", applyFilters),
  );
  controls.reset.addEventListener("click", () => {
    controls.search.value = "";
    controls.stage.value = "all";
    controls.group.value = "all";
    controls.status.value = "current";
    applyFilters();
    controls.search.focus();
  });
  detail.close.addEventListener("click", () => closeDetail());
  detail.backdrop.addEventListener("click", () => closeDetail());
  detail.copy.addEventListener("click", copySelectedLink);
  window.addEventListener("hashchange", openHashSelection);
  window.addEventListener("resize", scheduleDraw);
  document.addEventListener("keydown", (event) => {
    if (detail.panel.hidden) return;
    if (event.key === "Escape") {
      event.preventDefault();
      closeDetail();
      return;
    }
    if (event.key !== "Tab") return;
    const focusable = [
      ...detail.panel.querySelectorAll(
        'button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])',
      ),
    ].filter((element) => !element.hidden);
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });

  if ("ResizeObserver" in window) new ResizeObserver(scheduleDraw).observe(map);
  if (document.fonts?.ready) document.fonts.ready.then(scheduleDraw);
  applyFilters();
  openHashSelection();
})();
