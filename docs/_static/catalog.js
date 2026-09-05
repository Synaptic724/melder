"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("example-filters");
  if (!form) return; // The filter form exists only on the complete catalog page.
  const search = document.getElementById("example-search");
  const level = document.getElementById("example-level");
  const topic = document.getElementById("example-topic");
  const status = document.getElementById("example-results");
  const lessons = [...document.querySelectorAll(".example-item")];
  const parameters = new URLSearchParams(window.location.search);
  search.value = parameters.get("q") || "";
  level.value = parameters.get("level") || "";
  topic.value = parameters.get("topic") || "";
  const apply = () => {
    const words = search.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const lesson of lessons) {
      const matches = (!level.value || lesson.dataset.level === level.value)
        && (!topic.value || JSON.parse(lesson.dataset.topics).includes(topic.value))
        && words.every(word => lesson.dataset.search.includes(word));
      lesson.hidden = !matches;
      if (matches) visible += 1;
    }
    status.textContent = `${visible} of ${lessons.length} examples`;
    const query = new URLSearchParams();
    if (search.value.trim()) query.set("q", search.value.trim());
    if (level.value) query.set("level", level.value);
    if (topic.value) query.set("topic", topic.value);
    const suffix = query.size ? `?${query}` : "";
    history.replaceState(null, "", `${window.location.pathname}${suffix}${window.location.hash}`);
  };
  form.addEventListener("input", apply);
  form.addEventListener("change", apply);
  form.addEventListener("submit", event => { event.preventDefault(); apply(); });
  form.addEventListener("reset", () => requestAnimationFrame(apply));
  apply();
});
