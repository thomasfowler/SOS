// Actual vs Forecast vs Budget
function drawChart(chartType, canvasId, data, chartOptions = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.log(`Canvas with ID ${canvasId} not found`);
        return;
    }

    const ctx = canvas.getContext('2d');

    return new Chart(ctx, {
        type: chartType,
        data: data,
        options: chartOptions
    });
}

