(function () {
  "use strict";

  const nextFrame = () => new Promise((resolve) => requestAnimationFrame(resolve));

  function assetsAreReady(deck) {
    const images = Array.from(deck.querySelectorAll("img"));
    const graphs = Array.from(deck.querySelectorAll(".dash-graph"));
    return (
      images.every((image) => image.complete && image.naturalWidth > 0) &&
      graphs.every((graph) => graph.querySelector(".js-plotly-plot .main-svg"))
    );
  }

  async function waitForAssets(deck, timeoutMs) {
    const started = Date.now();
    while (!assetsAreReady(deck) && Date.now() - started < timeoutMs) {
      await nextFrame();
    }
    if (document.fonts && document.fonts.ready) {
      await document.fonts.ready;
    }
    await nextFrame();
    await nextFrame();
  }

  window.dash_clientside = Object.assign({}, window.dash_clientside, {
    workshop: {
      exportPdf: async function (trigger) {
        if (!trigger) {
          return window.dash_clientside.no_update;
        }

        const deck = document.getElementById("print-deck");
        const button = document.getElementById("pdf-export-button");
        if (!deck || !deck.children.length) {
          return window.dash_clientside.no_update;
        }

        const label = button && button.querySelector(".pdf-export-label");
        if (button) {
          button.disabled = true;
          button.setAttribute("aria-busy", "true");
        }
        if (label) {
          label.textContent = "Preparing…";
        }

        await waitForAssets(deck, 15000);
        document.body.classList.add("workshop-printing");

        try {
          window.print();
        } finally {
          document.body.classList.remove("workshop-printing");
          if (button) {
            button.disabled = false;
            button.removeAttribute("aria-busy");
          }
          if (label) {
            label.textContent = "Export PDF";
          }
        }

        return trigger;
      },
    },
  });
})();
