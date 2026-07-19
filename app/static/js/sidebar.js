const sidebar = document.getElementById("sidebar");
const backdrop = document.getElementById("sidebar-backdrop");
const openButton = document.getElementById("sidebar-toggle");
const closeButton = document.getElementById("sidebar-close");

function openSidebar() {
  sidebar.classList.remove("-translate-x-full");
  backdrop.classList.remove("hidden");
}

function closeSidebar() {
  sidebar.classList.add("-translate-x-full");
  backdrop.classList.add("hidden");
}

if (openButton) openButton.addEventListener("click", openSidebar);
if (closeButton) closeButton.addEventListener("click", closeSidebar);
if (backdrop) backdrop.addEventListener("click", closeSidebar);
