(function () {
  "use strict";

  var header = document.querySelector(".site-header");
  var toggle = document.querySelector(".nav-toggle");

  if (toggle && header) {
    toggle.addEventListener("click", function () {
      var isOpen = header.classList.toggle("open");
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
      if (!isOpen) closeAllSubmenus();
    });
  }

  function closeAllSubmenus(except) {
    document.querySelectorAll("li.has-children.open").forEach(function (li) {
      if (li !== except) {
        li.classList.remove("open");
        var btn = li.querySelector("button.nav-parent");
        if (btn) btn.setAttribute("aria-expanded", "false");
      }
    });
  }

  document.querySelectorAll("button.nav-parent").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var li = btn.closest("li.has-children");
      var willOpen = !li.classList.contains("open");
      closeAllSubmenus(willOpen ? li : null);
      li.classList.toggle("open", willOpen);
      btn.setAttribute("aria-expanded", willOpen ? "true" : "false");
    });
  });

  document.addEventListener("click", function (e) {
    if (!e.target.closest("nav.primary-nav")) closeAllSubmenus();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeAllSubmenus();
  });

  // Mark the current page's nav link.
  var here = window.location.pathname.replace(/\/index\.html$/, "/");
  document.querySelectorAll("nav.primary-nav a[href]").forEach(function (link) {
    var href = link.getAttribute("href");
    if (!href || href === "/") return;
    var normalized = href.replace(/\/index\.html$/, "/");
    if (here === normalized || here.indexOf(normalized) === 0) {
      link.setAttribute("aria-current", "page");
      var parentLi = link.closest("li.has-children");
      if (parentLi) {
        var parentBtn = parentLi.querySelector("button.nav-parent");
        if (parentBtn) parentBtn.setAttribute("aria-current", "page");
      }
    }
  });

  var year = document.querySelector("[data-year]");
  if (year) year.textContent = new Date().getFullYear();
})();
