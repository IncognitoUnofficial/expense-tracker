const data = window.DASHBOARD_DATA;

const palette = {
  ink: "#14151a",
  paper: "#ece7de",
  graphite: "#8d8b82",
  signal: "#d4a13d",
  wire: "#4a6b5a",
};

const categoryCanvas = document.getElementById("categoryChart");
if (categoryCanvas && data.categoryLabels.length) {
  new Chart(categoryCanvas, {
    type: "doughnut",
    data: {
      labels: data.categoryLabels,
      datasets: [
        {
          data: data.categoryTotals,
          backgroundColor: [palette.wire, palette.signal, palette.graphite, palette.ink, "#7c9c8a", "#e0bc70"],
          borderWidth: 0,
        },
      ],
    },
    options: {
      plugins: { legend: { display: false } },
    },
  });
}

const trendCanvas = document.getElementById("trendChart");
if (trendCanvas) {
  new Chart(trendCanvas, {
    type: "bar",
    data: {
      labels: data.trendLabels,
      datasets: [
        {
          label: "Total spend",
          data: data.trendTotals,
          backgroundColor: palette.wire,
          borderRadius: 4,
        },
      ],
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, ticks: { color: palette.graphite } },
        x: { ticks: { color: palette.graphite } },
      },
    },
  });
}
