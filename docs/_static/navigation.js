"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const button = document.getElementById("melder-menu-toggle");
  const sidebar = document.querySelector("nav.wy-nav-side");
  if (!button || !sidebar) {
    throw new Error("Melder navigation template is missing its menu control or sidebar.");
  }
  const updateState = () => {
    const wasOpen = button.getAttribute("aria-expanded") === "true";
    const isOpen = sidebar.classList.contains("shift");
    button.setAttribute("aria-expanded", String(isOpen));
    if (!window.matchMedia("(max-width: 768px)").matches) return;
    if (isOpen && !wasOpen) {
      sidebar.querySelector("a[href], input, button").focus();
    } else if (!isOpen && wasOpen && sidebar.contains(document.activeElement)) {
      button.focus();
    }
  };
  new MutationObserver(updateState).observe(sidebar, { attributes: true, attributeFilter: ["class"] });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && sidebar.classList.contains("shift")
        && window.matchMedia("(max-width: 768px)").matches) {
      event.preventDefault();
      // Reuse the theme's toggle handler instead of maintaining a second drawer state.
      button.click();
      button.focus();
    }
  });
  document.addEventListener("focusin", event => {
    if (sidebar.classList.contains("shift") && window.matchMedia("(max-width: 768px)").matches
        && !sidebar.contains(event.target) && event.target !== button) {
      // Leaving this non-modal drawer must not strand focus in the shifted-offscreen page.
      button.click();
    }
  });
  updateState();
});
