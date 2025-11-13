(function () {
  try {
    const dataElement = document.getElementById("usages-by-date");
    if (!dataElement) {
      console.warn("Element 'usages-by-date' not found");
      return;
    }

    const raw = dataElement.textContent;
    const dataObj = JSON.parse(raw || "{}");
    const labels = Object.keys(dataObj).sort();
    const values = labels.map((d) => dataObj[d] || 0);

    const canvas = document.getElementById("usagesChart");
    if (!canvas) {
      console.warn("Canvas 'usagesChart' not found");
      return;
    }

    const ctx = canvas.getContext("2d");
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Використання",
            data: values,
            backgroundColor: "rgba(13, 148, 136, 0.9)",
            borderRadius: 6,
            barThickness: 40,
            maxBarThickness: 50,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        aspectRatio: 2.5,
        scales: {
          x: {
            ticks: {
              color: "#374151",
              font: { size: 11 },
            },
          },
          y: {
            beginAtZero: true,
            ticks: {
              color: "#374151",
              font: { size: 11 },
            },
          },
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            padding: 8,
            bodyFont: { size: 12 },
          },
        },
      },
    });
  } catch (e) {
    console.error("Chart render error:", e);
  }
})();
