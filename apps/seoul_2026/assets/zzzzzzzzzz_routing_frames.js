/* Load only the selected technology's potentially large routed graph. */
(function () {
  'use strict';
  function sync() {
    document.querySelectorAll('.route-frame').forEach(frame => {
      const active = !frame.closest('[hidden]');
      const next = active ? frame.dataset.routeSrc : 'about:blank';
      if (frame.getAttribute('src') !== next) frame.setAttribute('src', next);
    });
  }
  function start() {
    new MutationObserver(sync).observe(document.body, {childList:true, subtree:true, attributes:true, attributeFilter:['hidden']});
    sync();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
