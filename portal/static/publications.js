(() => {
  const root = document.querySelector("[data-publications]");
  if (!root) return;

  const search = root.querySelector("#publication-search");
  const year = root.querySelector("#publication-year");
  const topic = root.querySelector("#publication-topic");
  const reset = root.querySelector("#publication-reset");
  const resultCount = root.querySelector("#publication-result-count");
  const empty = root.querySelector("#publication-empty");
  const list = root.querySelector("#publications-list");
  const items = [...root.querySelectorAll("[data-publication-item]")];
  const total = items.length;

  const normalize = (value) =>
    value
      .trim()
      .toLocaleLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");

  const applyFilters = () => {
    const query = normalize(search.value);
    const selectedYear = year.value;
    const selectedTopic = normalize(topic.value);
    let visible = 0;

    items.forEach((item) => {
      const searchable = normalize(item.dataset.search || "");
      const topics = normalize(item.dataset.topics || "").split("|");
      const matches =
        (!query || searchable.includes(query)) &&
        (!selectedYear || item.dataset.year === selectedYear) &&
        (!selectedTopic || topics.includes(selectedTopic));
      item.hidden = !matches;
      if (matches) visible += 1;
    });

    const filtersActive = Boolean(query || selectedYear || selectedTopic);
    resultCount.textContent = filtersActive
      ? `${visible} of ${total} publications`
      : `${total} verified publications`;
    empty.hidden = visible !== 0;
    list.hidden = visible === 0;
    reset.disabled = !filtersActive;
    list.scrollTop = 0;
  };

  search.addEventListener("input", applyFilters);
  year.addEventListener("change", applyFilters);
  topic.addEventListener("change", applyFilters);
  reset.addEventListener("click", () => {
    search.value = "";
    year.value = "";
    topic.value = "";
    applyFilters();
    search.focus();
  });
})();
