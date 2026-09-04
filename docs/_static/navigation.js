"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const button = document.getElementById("melder-menu-toggle");
  const sidebar = document.querySelector("nav.wy-nav-side");
  if (!button || !sidebar) {
    throw new Error("Melder navigation template is missing its menu control or sidebar.");
  }
  const updateState = () => {
    button.setAttribute("aria-expanded", String(sidebar.classList.contains("shift")));
  };
  new MutationObserver(updateState).observe(sidebar, { attributes: true, attributeFilter: ["class"] });
  updateState();
});
