(function () {
  "use strict";
  const key = "mcv-2026-slide";
  const frame = () => new Promise(resolve => requestAnimationFrame(resolve));

  document.addEventListener("keydown", function (event) {
    const target = event.target;
    if (event.altKey || event.ctrlKey || event.metaKey ||
        target.closest("input, textarea, select, button, a, [role=slider], [contenteditable=true]")) return;
    const next = ["ArrowRight", "PageDown", " "].includes(event.key);
    const previous = ["ArrowLeft", "PageUp"].includes(event.key);
    if (next || previous) {
      event.preventDefault();
      document.getElementById(next ? "next-button" : "previous-button")?.click();
    }
  });
  document.addEventListener("click", async function (event) {
    if (!event.target.closest("#fullscreen-button")) return;
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
    } catch (error) {
      document.getElementById("print-status").textContent = "Le plein écran est indisponible dans ce navigateur.";
    }
  });

  window.dash_clientside = Object.assign({}, window.dash_clientside, {
    mcv: {
      syncSlide: function (index) {
        try { localStorage.setItem(key, JSON.stringify({ index: index, at: Date.now() })); } catch (_) {}
        return index;
      },
      exportPdf: async function (trigger) {
        if (!trigger) return window.dash_clientside.no_update;
        const status = document.getElementById("print-status");
        const deck = document.getElementById("print-deck");
        const title = document.title;
        const restoreTitle = () => { document.title = title; };
        status.textContent = `Préparation du PDF de ${trigger.slide_count} diapositives…`;
        deck.dataset.ready = "false";
        try {
          await document.fonts.ready;
          await frame();
          // Dash may still be mounting graphs and loading images.
          const deadline = Date.now() + 30000;
          let ready = false;
          while (Date.now() < deadline) {
            const roots = Array.from(deck.querySelectorAll(".dash-graph"));
            const imagesReady = Array.from(deck.querySelectorAll("img")).every(img => img.complete && img.naturalWidth > 0);
            ready = imagesReady && roots.length === trigger.graph_count && roots.every(root => {
              const plot = root.querySelector(".js-plotly-plot");
              return plot && plot._fullLayout && !root.hasAttribute("data-dash-is-loading");
            });
            if (ready) break;
            await new Promise(resolve => setTimeout(resolve, 100));
          }
          if (!ready) throw new Error("Les graphiques ou les images ne sont pas prêts. Relancez l’export PDF.");
          for (const plot of deck.querySelectorAll(".js-plotly-plot")) {
            await window.Plotly.Plots.resize(plot);
          }
          await frame();
          await frame();
          document.title = trigger.filename;
          deck.dataset.ready = "true";
          status.textContent = "Choisir Enregistrer au format PDF · paysage · sans en-têtes ni pieds de page.";
          window.addEventListener("afterprint", restoreTitle, { once: true });
          window.print();
          return trigger.click;
        } catch (error) {
          window.removeEventListener("afterprint", restoreTitle);
          restoreTitle();
          status.textContent = error.message;
          return window.dash_clientside.no_update;
        }
      }
    }
  });
})();
