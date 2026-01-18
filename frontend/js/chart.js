/**
 * Chart rendering using Chart.js
 */

let chartInstance = null;

function renderShapChart(featureNames, shapValues) {
    // Get top 5 features by absolute SHAP value
    const combined = featureNames.map((name, index) => ({
        name: name,
        value: shapValues[index]
    }));
    
    // Sort by absolute value
    combined.sort((a, b) => Math.abs(b.value) - Math.abs(a.value));
    const top5 = combined.slice(0, 5);
    
    // Prepare data for chart
    const labels = top5.map(item => item.name);
    const data = top5.map(item => item.value);
    const colors = data.map(val => val > 0 ? '#ef4444' : '#10b981');
    
    // Get canvas
    const canvas = document.getElementById('shapChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Destroy previous chart if exists
    if (chartInstance) {
        chartInstance.destroy();
    }
    
    // Create new chart
    chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderRadius: 6,
                barThickness: 32
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed.x;
                            const impact = value > 0 ? 'increases' : 'decreases';
                            return `${impact} churn risk by ${Math.abs(value).toFixed(3)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: '#f1f5f9'
                    },
                    ticks: {
                        color: '#64748b'
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#1e293b',
                        font: {
                            weight: 500
                        }
                    }
                }
            }
        }
    });
}
