(function () {
  "use strict";

  const nextFrame = () => new Promise((resolve) => requestAnimationFrame(resolve));
  let prospectiveHoverSyncing = false;

  window.dash_clientside = Object.assign({}, window.dash_clientside, {
    workshop: {
      syncProspectiveHover: function (beccsHover, daccsHover) {
        const triggered = window.dash_clientside.callback_context.triggered || [];
        if (!triggered.length || prospectiveHoverSyncing) {
          return window.dash_clientside.no_update;
        }
        const source = triggered[0].prop_id.split(".")[0];
        const hover = source === "prospective-beccs-chart" ? beccsHover : daccsHover;
        const targetId = source === "prospective-beccs-chart"
          ? "prospective-daccs-chart"
          : "prospective-beccs-chart";
        const targetRoot = document.getElementById(targetId);
        const target = targetRoot && targetRoot.querySelector(".js-plotly-plot");
        if (!target || !window.Plotly) {
          return window.dash_clientside.no_update;
        }
        prospectiveHoverSyncing = true;
        if (hover && hover.points && hover.points.length) {
          const pointNumber = hover.points[0].pointNumber;
          window.Plotly.Fx.hover(target, [{ curveNumber: 0, pointNumber: pointNumber }]);
        } else {
          window.Plotly.Fx.unhover(target);
        }
        window.setTimeout(() => {
          prospectiveHoverSyncing = false;
        }, 60);
        return { source: source, timestamp: Date.now() };
      },
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
        document.body.classList.add("workshop-printing");
        try {
          window.print();
        } finally {
          document.body.classList.remove("workshop-printing");
        }
        return trigger;
      },
    },
  });
})();
