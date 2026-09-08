/* lca_time-inspired live comparisons, kept beside the chart so a popup never
   hides an area. All interaction is with already calculated browser data. */
(function () {
  "use strict";
  const number = (value, unit) => new Intl.NumberFormat("en-GB", unit.includes("kg")
    ? {maximumFractionDigits: 0} : {maximumSignificantDigits: 3}).format(value);
  function bindCharts() {
    document.querySelectorAll(".result-layout .js-plotly-plot").forEach(gd => {
      if (!gd.on || gd.dataset.comparisonBound) return;
      const layout = gd.closest(".result-layout");
      const readout = layout.querySelector(".chart-reading");
      if (!readout) return;
      gd.dataset.comparisonBound = "true";
      gd.on("plotly_hover", event => {
        const rows = gd.layout.meta?.readouts;
        const point = event.points?.[0];
        const yearLabel = readout.querySelector(".reading-year");
        const values = readout.querySelector(".reading-values");
        if (!rows || !point || !yearLabel || !values || !readout.isConnected) return;
        const year = Number(point.x);
        yearLabel.textContent =
          (gd.layout.meta.presentation_kind === "pulse" ? "Window closes " : "Year ") + Math.floor(year);
        values.replaceChildren(...rows.map(row => {
          let nearest = 0;
          row.x.forEach((x, i) => { if (Math.abs(x - year) < Math.abs(row.x[nearest] - year)) nearest = i; });
          const item = document.createElement("span");
          const label = document.createElement("b");
          label.textContent = row.system + " ";
          item.append(label, number(row.y[nearest], row.unit) + " " + row.unit);
          return item;
        }));
        if (point.data?.meta?.annual) {
          const axis = point.data.yaxis || "y";
          const series = gd.data.filter(t => t.meta?.annual && (t.yaxis || "y") === axis && t.legendgroup === point.data.legendgroup);
          const contribution = series.reduce((total,t) => {
            const i = t.x.findIndex(x => Number(x) === year);
            return total + (i < 0 ? 0 : Number(t.y[i]));
          },0);
          const item = document.createElement("span");
          item.className = "reading-contribution";
          item.textContent = point.data.meta.system + " · " + point.data.name + ": " + number(contribution,"kg") + " " + point.data.meta.unit;
          values.append(item);
        }
      });
      const focus = readout.querySelector(".chart-focus");
      if (focus) focus.onclick = () => {
        const update = {};
        Object.keys(gd.layout.meta?.reset_axes || {}).filter(key => key.startsWith("xaxis")).forEach(key => { update[key + ".range"] = [2025,2070]; });
        window.Plotly.relayout(gd,update);
      };
      const reset = readout.querySelector(".chart-reset");
      if (reset) reset.onclick = () => {
        const update = {};
        Object.entries(gd.layout.meta?.reset_axes || {}).forEach(([key, range]) => {
          update[key + (range ? ".range" : ".autorange")] = range || true;
        });
        window.Plotly.restyle(gd, {visible: true});
        window.Plotly.relayout(gd, update);
        const yearLabel = readout.querySelector(".reading-year");
        const values = readout.querySelector(".reading-values");
        if (yearLabel) yearLabel.textContent = "Move along a curve to compare one year.";
        if (values) values.replaceChildren();
      };
    });
  }
  let scheduled = false;
  const observer = new MutationObserver(() => {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => { scheduled = false; bindCharts(); });
  });
  function start() { observer.observe(document.body, {childList:true,subtree:true}); bindCharts(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
