(function () {
  "use strict";

  const nextFrame = () => new Promise((resolve) => requestAnimationFrame(resolve));

  // Public helper also used by the deterministic browser/PDF audit.
  window.ccusPreparePrint = async function () {
    document.body.classList.add("ccus-webinar-printing");
    if (document.fonts && document.fonts.ready) await document.fonts.ready;
    await nextFrame();
    await nextFrame();
    const graphs = document.querySelectorAll("#print-deck .js-plotly-plot");
    await Promise.all(Array.from(graphs, gd => {
      const bounds = gd.closest(".dash-graph").getBoundingClientRect();
      if (!bounds.width || !bounds.height) return Promise.resolve();
      return window.Plotly.relayout(gd, {width: bounds.width, height: bounds.height});
    }));
    await nextFrame();
  };

  window.dash_clientside = Object.assign({}, window.dash_clientside, {
    ccusWebinar: {
      exportPdf: async function (trigger) {
        if (!trigger) {
          return window.dash_clientside.no_update;
        }
        const deck = document.getElementById("print-deck");
        if (!deck || !deck.children.length) {
          return window.dash_clientside.no_update;
        }
        if (document.fonts && document.fonts.ready) {
          await document.fonts.ready;
        }
        await nextFrame();
        await nextFrame();
        try {
          await window.ccusPreparePrint();
          window.print();
        } finally {
          document.body.classList.remove("ccus-webinar-printing");
        }
        return trigger;
      },
    },
  });
})();
