const root = document.documentElement;
const toggleButton = document.getElementById("theme-toggle");
const sunIcon = document.getElementById("theme-icon-sun");
const moonIcon = document.getElementById("theme-icon-moon");
const label = document.getElementById("theme-toggle-label");

function syncThemeUI() {
  const isDark = root.classList.contains("dark");
  if (sunIcon && moonIcon && label) {
    sunIcon.classList.toggle("hidden", isDark);
    moonIcon.classList.toggle("hidden", !isDark);
    label.textContent = isDark ? "Light mode" : "Dark mode";
  }
}

syncThemeUI();

if (toggleButton) {
  toggleButton.addEventListener("click", () => {
    root.classList.toggle("dark");
    localStorage.setItem("theme", root.classList.contains("dark") ? "dark" : "light");
    syncThemeUI();
  });
}
