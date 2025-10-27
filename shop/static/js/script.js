document.addEventListener("DOMContentLoaded", function () {
  const burger = document.getElementById("burgerBtn");
  const menu = document.getElementById("mobileMenu");
  const overlay = document.getElementById("mobileOverlay");
  const closeBtn = document.getElementById("closeMenuBtn");

  function openMenu() {
    if (menu) menu.classList.add("open");
    if (overlay) overlay.classList.remove("hidden");
    document.body.classList.add("menu-open");
  }

  function closeMenu() {
    if (menu) menu.classList.remove("open");
    if (overlay) overlay.classList.add("hidden");
    document.body.classList.remove("menu-open");
  }

  if (burger) burger.addEventListener("click", openMenu);
  if (closeBtn) closeBtn.addEventListener("click", closeMenu);
  if (overlay) overlay.addEventListener("click", closeMenu);

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeMenu();
  });

  const desktopBtn = document.getElementById("categoriesBtnDesktop");
  const desktopDropdown = document.getElementById("categoriesDropdownDesktop");

  if (desktopBtn && desktopDropdown) {
    desktopBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      desktopDropdown.classList.toggle("hidden");
    });
    document.addEventListener("click", function (e) {
      if (!desktopDropdown.contains(e.target) && e.target !== desktopBtn) {
        desktopDropdown.classList.add("hidden");
      }
    });
  }
});