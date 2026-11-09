(function () {
  "use strict";
  const key = "kent-2026-slide";
  const frame = () => new Promise(resolve => requestAnimationFrame(resolve));
  let zoomReturnFocus = null;
  let familyZoomReturnFocus = null;

  function zoomModal() {
    let modal = document.getElementById("capability-zoom-modal");
    if (modal) return modal;
    modal = document.createElement("div");
    modal.id = "capability-zoom-modal";
    modal.className = "capability-zoom-modal";
    modal.hidden = true;
    modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");
    modal.setAttribute("aria-labelledby", "capability-zoom-title");
    modal.innerHTML = '<div class="capability-zoom-dialog"><div class="capability-zoom-header"><h2 id="capability-zoom-title" class="capability-zoom-title"></h2><button type="button" class="capability-zoom-close" aria-label="Close enlarged tile">×</button></div><div class="capability-zoom-crop" role="img"></div></div>';
    document.body.appendChild(modal);
    return modal;
  }

  function closeZoom() {
    const modal = document.getElementById("capability-zoom-modal");
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    document.body.classList.remove("capability-modal-open");
    zoomReturnFocus?.focus();
    zoomReturnFocus = null;
  }

  function familyZoomModal() {
    let modal = document.getElementById("family-zoom-modal");
    if (modal) return modal;
    modal = document.createElement("div");
    modal.id = "family-zoom-modal";
    modal.className = "family-zoom-modal";
    modal.hidden = true;
    modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");
    modal.setAttribute("aria-labelledby", "family-zoom-title");
    modal.innerHTML = '<div class="family-zoom-dialog"><div class="family-zoom-header"><h2 id="family-zoom-title" class="family-zoom-title"></h2><button type="button" class="family-zoom-close" aria-label="Close enlarged comparison">×</button></div><div class="family-zoom-content"></div></div>';
    document.body.appendChild(modal);
    return modal;
  }

  function openFamilyZoom(card) {
    const modal = familyZoomModal();
    const clone = card.cloneNode(true);
    const legend = card.closest(".mobility-comparison-layout")?.querySelector(".mobility-stage-legend")?.cloneNode(true);
    familyZoomReturnFocus = card;
    clone.classList.add("family-zoomed-card");
    clone.removeAttribute("role");
    clone.removeAttribute("tabindex");
    clone.removeAttribute("title");
    clone.removeAttribute("data-family-zoom");
    clone.removeAttribute("data-family-title");
    clone.removeAttribute("aria-label");
    clone.querySelector(".mobility-family-zoom-icon")?.remove();
    modal.querySelector(".family-zoom-title").textContent = `${card.dataset.familyTitle} · life-cycle contributions`;
    const content = modal.querySelector(".family-zoom-content");
    content.replaceChildren(...(legend ? [legend, clone] : [clone]));
    modal.hidden = false;
    document.body.classList.add("family-modal-open");
    modal.querySelector(".family-zoom-close").focus();
  }

  function closeFamilyZoom() {
    const modal = document.getElementById("family-zoom-modal");
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    document.body.classList.remove("family-modal-open");
    familyZoomReturnFocus?.focus();
    familyZoomReturnFocus = null;
  }

  document.addEventListener("keydown", function (event) {
    const activeFamilyModal = document.getElementById("family-zoom-modal");
    if (event.key === "Escape" && activeFamilyModal && !activeFamilyModal.hidden) {
      event.preventDefault();
      closeFamilyZoom();
      return;
    }
    const activeCapabilityModal = document.getElementById("capability-zoom-modal");
    if (event.key === "Escape" && activeCapabilityModal && !activeCapabilityModal.hidden) {
      event.preventDefault();
      closeZoom();
      return;
    }
    const target = event.target;
    const familyCard = target.closest?.("[data-family-zoom]");
    if (familyCard && (event.key === "Enter" || event.key === " ")) {
      event.preventDefault();
      openFamilyZoom(familyCard);
      return;
    }
    if (event.altKey || event.ctrlKey || event.metaKey || target.closest("input, textarea, select, button, a, [role=slider], [contenteditable=true]")) return;
    const next = ["ArrowRight", "PageDown", " "].includes(event.key);
    const previous = ["ArrowLeft", "PageUp"].includes(event.key);
    if (next || previous) {
      event.preventDefault();
      document.getElementById(next ? "next-button" : "previous-button")?.click();
    }
  });
  document.addEventListener("click", async function (event) {
    const zoomButton = event.target.closest(".capability-zoom-button");
    if (zoomButton) {
      const modal = zoomModal();
      const title = zoomButton.dataset.zoomTitle;
      const crop = modal.querySelector(".capability-zoom-crop");
      zoomReturnFocus = zoomButton;
      modal.querySelector(".capability-zoom-title").textContent = title;
      crop.dataset.tile = zoomButton.dataset.zoomTile;
      crop.setAttribute("aria-label", `Enlarged ${title.toLowerCase()}`);
      modal.hidden = false;
      document.body.classList.add("capability-modal-open");
      modal.querySelector(".capability-zoom-close").focus();
      return;
    }
    if (event.target.closest(".capability-zoom-close") || event.target.id === "capability-zoom-modal") {
      closeZoom();
      return;
    }
    const familyCard = event.target.closest("[data-family-zoom]");
    if (familyCard) {
      openFamilyZoom(familyCard);
      return;
    }
    if (event.target.closest(".family-zoom-close") || event.target.id === "family-zoom-modal") {
      closeFamilyZoom();
      return;
    }
    if (!event.target.closest("#fullscreen-button")) return;
    if (document.fullscreenElement) await document.exitFullscreen();
    else await document.documentElement.requestFullscreen();
  });

  window.dash_clientside = Object.assign({}, window.dash_clientside, {
    kent: {
      syncSlide: function (index) {
        try { localStorage.setItem(key, JSON.stringify({ index: index, at: Date.now() })); } catch (_) {}
        return index;
      },
      exportPdf: async function (trigger) {
        if (!trigger) return window.dash_clientside.no_update;
        const status = document.getElementById("print-status");
        const deck = document.getElementById("print-deck");
        const original = document.title;
        status.textContent = `Preparing ${trigger.slide_count} pages…`;
        try {
          await document.fonts.ready;
          const deadline = Date.now() + 30000;
          let ready = false;
          while (Date.now() < deadline) {
            const loading = deck.querySelector("[data-dash-is-loading=true]");
            const roots = Array.from(deck.querySelectorAll(".dash-graph"));
            ready = !loading && roots.length === trigger.graph_count && roots.every(root => root.querySelector(".js-plotly-plot"));
            if (ready) break;
            await new Promise(resolve => setTimeout(resolve, 100));
          }
          if (!ready) throw new Error("The PDF charts did not finish rendering. Please try again.");
          for (const plot of deck.querySelectorAll(".js-plotly-plot")) await window.Plotly.Plots.resize(plot);
          await frame(); await frame();
          document.title = trigger.filename;
          document.body.classList.add("printing-deck");
          status.textContent = "Choose Save as PDF · landscape · backgrounds enabled.";
          window.print();
          return trigger.click;
        } finally {
          document.title = original;
          document.body.classList.remove("printing-deck");
        }
      }
    }
  });
})();

