const searchInput = document.getElementById("search-input");

if (searchInput) {
  let debounceTimer;
  searchInput.addEventListener("input", () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      document.getElementById("filter-form").submit();
    }, 500);
  });
}
