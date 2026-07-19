document.addEventListener("submit", (event) => {
  const form = event.target.closest("form[data-confirm]");
  if (form && !window.confirm(form.dataset.confirm)) {
    event.preventDefault();
  }
});

document.querySelectorAll("[data-toggle-edit]").forEach((button) => {
  button.addEventListener("click", () => {
    const row = button.closest("[data-category-row]");
    row.querySelectorAll("[data-display]").forEach((el) => el.classList.toggle("hidden"));
    row.querySelector("[data-edit-form]").classList.toggle("hidden");
  });
});
