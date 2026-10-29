(function () {
  "use strict";
  const key = "snu-2026-slide";
  const frame = () => new Promise(resolve => requestAnimationFrame(resolve));

  function selectLesson(lesson, index, focus = false) {
    const tabs = Array.from(lesson.querySelectorAll(':scope > .lesson-tabs [data-lesson-select]'));
    index = (index + tabs.length) % tabs.length;
    lesson.dataset.lessonIndex = String(index);
    tabs.forEach((tab, i) => {
      tab.setAttribute('aria-selected', String(i === index));
      tab.tabIndex = i === index ? 0 : -1;
    });
    Array.from(lesson.children).filter(el => el.hasAttribute('data-lesson-panel'))
      .forEach((panel, i) => { panel.hidden = i !== index; });
    // Reused charts remain mounted while hidden; resize after revealing them.
    requestAnimationFrame(() => {
      window.dispatchEvent(new Event('resize'));
      lesson.querySelectorAll('[data-lesson-panel]:not([hidden]) .js-plotly-plot')
        .forEach(plot => { if (plot._fullLayout) window.Plotly?.Plots.resize(plot); });
    });
    if (focus) tabs[index].focus();
  }
  document.addEventListener('click', function (event) {
    const tab = event.target.closest('[data-lesson-select]');
    if (tab) selectLesson(tab.closest('.lesson-switch'), Number(tab.dataset.lessonSelect));
  });
  document.addEventListener('keydown', function (event) {
    const tab = event.target.closest('[data-lesson-select]');
    if (!tab || !['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    const lesson = tab.closest('.lesson-switch');
    const last = lesson.querySelectorAll(':scope > .lesson-tabs [data-lesson-select]').length - 1;
    const index = event.key === 'Home' ? 0 : event.key === 'End' ? last
      : Number(tab.dataset.lessonSelect) + (event.key === 'ArrowRight' ? 1 : -1);
    selectLesson(lesson, index, true);
  });

  // Keep the three-date control keyboard-operable with this rc-slider version.
  // Use the focused handle's date, rather than the library's last-dragged index.
  document.addEventListener('keydown', function (event) {
    const handle = event.target.closest('#equivalence-window .rc-slider-handle');
    if (!handle || !['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'].includes(event.key)
        || typeof window.dash_clientside?.set_props !== 'function') return;
    event.preventDefault();
    event.stopPropagation();
    const handles = Array.from(document.querySelectorAll('#equivalence-window .rc-slider-handle'));
    const dates = handles.map(el => Number(el.getAttribute('aria-valuenow')));
    const index = handles.indexOf(handle);
    const low = index === 0 ? 2000 : dates[index - 1] + 5;
    const high = index === 2 ? 2300 : dates[index + 1] - 5;
    const next = event.key === 'Home' ? low : event.key === 'End' ? high
      : dates[index] + (['ArrowRight', 'ArrowUp'].includes(event.key) ? 5 : -5);
    dates[index] = Math.max(low, Math.min(high, next));
    window.dash_clientside.set_props('equivalence-window', { value: dates });
  }, true);
  document.addEventListener('focusin', function (event) {
    const handle = event.target.closest('#equivalence-window .rc-slider-handle');
    if (!handle) return;
    const index = Array.from(document.querySelectorAll('#equivalence-window .rc-slider-handle')).indexOf(handle);
    handle.setAttribute('aria-label', ['Window start year', 'Reference pulse year', 'Window end year'][index]);
    // rc-slider's focus handler starts a drag and can shift a neighbouring date.
    // Pointer dragging has its own mousedown handler; focus alone must be passive.
    event.stopPropagation();
  }, true);

  function selectProcess(carousel, index, focus = false) {
    const tabs = Array.from(carousel.querySelectorAll('[data-process-select]'));
    index = (index + tabs.length) % tabs.length;
    carousel.dataset.processIndex = String(index);
    tabs.forEach((tab, i) => {
      tab.setAttribute('aria-selected', String(i === index));
      tab.tabIndex = i === index ? 0 : -1;
    });
    carousel.querySelectorAll('[data-process-panel]').forEach((panel, i) => {
      panel.hidden = i !== index;
    });
    carousel.querySelector('.process-position').textContent = `${index + 1} / ${tabs.length}`;
    if (focus) tabs[index].focus();
  }
  document.addEventListener('click', function (event) {
    const control = event.target.closest('[data-process-select], [data-process-step]');
    if (!control) return;
    const carousel = control.closest('.process-carousel');
    const index = control.hasAttribute('data-process-select')
      ? Number(control.dataset.processSelect)
      : Number(carousel.dataset.processIndex) + Number(control.dataset.processStep);
    selectProcess(carousel, index);
  });
  document.addEventListener('keydown', function (event) {
    const tab = event.target.closest('[data-process-select]');
    if (!tab || !['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    const carousel = tab.closest('.process-carousel');
    const index = event.key === 'Home' ? 0 : event.key === 'End' ? 3
      : Number(carousel.dataset.processIndex) + (event.key === 'ArrowRight' ? 1 : -1);
    selectProcess(carousel, index, true);
  });

  document.addEventListener("keydown", function (event) {
    const target = event.target;
    if (event.altKey || event.ctrlKey || event.metaKey ||
        target.closest("input, textarea, select, button, a, summary, [role=slider], [contenteditable=true]")) return;
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
      document.getElementById("print-status").textContent = "Full screen is unavailable in this browser.";
    }
  });

  window.dash_clientside = Object.assign({}, window.dash_clientside, {
    snu: {
      syncSlide: function (index) {
        try { localStorage.setItem(key, JSON.stringify({ index: index, at: Date.now() })); } catch (_) {}
        // Keep a reload/bookmark on the slide actually shown after button navigation.
        history.replaceState(null, "", location.pathname + location.search + "#slide-" + index);
        let active = null;
        for (const button of document.querySelectorAll(".chapter-nav button")) {
          button.removeAttribute("aria-current");
          try { if (JSON.parse(button.id).slide <= index) active = button; } catch (_) {}
        }
        active?.setAttribute("aria-current", "page");
        return index;
      },
      exportPdf: async function (trigger) {
        if (!trigger) return window.dash_clientside.no_update;
        const status = document.getElementById("print-status");
        const deck = document.getElementById("print-deck");
        const title = document.title;
        status.textContent = `Preparing the ${trigger.slide_count}-page PDF…`;
        deck.dataset.ready = "false";
        document.body.classList.add("preparing-print");
        try {
          await document.fonts.ready;
          await Promise.all(Array.from(deck.querySelectorAll('img')).map(img => img.decode()));
          await frame();
          // Dash may still be mounting graphs when the callback is invoked.
          const deadline = Date.now() + 30000;
          let ready = false;
          while (Date.now() < deadline) {
            const roots = Array.from(deck.querySelectorAll(".dash-graph"));
            ready = roots.length === trigger.graph_count && roots.every(root => {
              const plot = root.querySelector(".js-plotly-plot");
              return plot && plot._fullLayout && !root.hasAttribute("data-dash-is-loading");
            });
            if (ready) break;
            await new Promise(resolve => setTimeout(resolve, 100));
          }
          if (!ready) throw new Error("The charts did not finish rendering. Please try Export PDF again.");
          for (const plot of deck.querySelectorAll(".js-plotly-plot")) {
            await window.Plotly.Plots.resize(plot);
          }
          await frame();
          await frame();
          document.title = trigger.filename;
          deck.dataset.ready = "true";
          status.textContent = "Choose Save as PDF · landscape · no headers or footers.";
          window.print();
          return trigger.click;
        } catch (error) {
          status.textContent = error.message;
          return window.dash_clientside.no_update;
        } finally {
          document.title = title;
          document.body.classList.remove("preparing-print");
          window.dispatchEvent(new Event("resize"));
        }
      }
    }
  });
})();
