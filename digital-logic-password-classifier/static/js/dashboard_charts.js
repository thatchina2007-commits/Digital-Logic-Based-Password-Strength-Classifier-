/**
 * dashboard_charts.js
 * EC2201 Digital Logic Design - Chart.js Visualizations
 * Renders Category Doughnut, Scores Histogram, and Attribute Fulfillment Bar charts.
 */

let categoryChart = null;
let scoreChart = null;
let attributeChart = null;

document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
});

async function initDashboard() {
    const statsContainer = document.getElementById('dashboardMetricsContainer');
    if (!statsContainer) return;

    try {
        const response = await fetch('/api/dashboard/stats');
        if (!response.ok) throw new Error('Failed to fetch dashboard stats');

        const data = await response.json();
        updateKPICards(data);
        renderCharts(data);
    } catch (err) {
        console.error('Error initializing dashboard:', err);
    }
}

function updateKPICards(data) {
    setText('kpi-total-evals', data.total);
    setText('kpi-avg-length', `${data.avg_length} chars`);
    setText('kpi-secure-pct', `${data.secure_percentage}%`);
    setText('kpi-weak-cnt', data.categories.Weak);
    setText('kpi-med-cnt', data.categories.Medium);
    setText('kpi-strong-cnt', data.categories.Strong);
    setText('kpi-vstrong-cnt', data.categories["Very Strong"]);
}

function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}

function renderCharts(data) {
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js is not loaded.');
        return;
    }

    // Neon Palette
    const colorWeak = '#ff3366';
    const colorMedium = '#ffb703';
    const colorStrong = '#00d2ff';
    const colorVeryStrong = '#00f5a0';

    // 1. Category Distribution Doughnut
    const ctxCat = document.getElementById('chartCategoryDistribution')?.getContext('2d');
    if (ctxCat) {
        if (categoryChart) categoryChart.destroy();
        categoryChart = new Chart(ctxCat, {
            type: 'doughnut',
            data: {
                labels: ['Weak', 'Medium', 'Strong', 'Very Strong'],
                datasets: [{
                    data: [
                        data.categories.Weak,
                        data.categories.Medium,
                        data.categories.Strong,
                        data.categories["Very Strong"]
                    ],
                    backgroundColor: [colorWeak, colorMedium, colorStrong, colorVeryStrong],
                    borderColor: '#070a13',
                    borderWidth: 2,
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#94a3b8', font: { family: 'inherit', size: 12 } }
                    }
                }
            }
        });
    }

    // 2. Score Histogram Bar Chart (0 to 5)
    const ctxScore = document.getElementById('chartScoreHistogram')?.getContext('2d');
    if (ctxScore) {
        if (scoreChart) scoreChart.destroy();
        scoreChart = new Chart(ctxScore, {
            type: 'bar',
            data: {
                labels: ['Score 0', 'Score 1', 'Score 2', 'Score 3', 'Score 4', 'Score 5'],
                datasets: [{
                    label: 'Password Count',
                    data: data.scores_histogram,
                    backgroundColor: [
                        colorWeak,
                        colorWeak,
                        colorMedium,
                        colorMedium,
                        colorStrong,
                        colorVeryStrong
                    ],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    // 3. Attribute Fulfillment Rate Bar Chart (A, B, C, D, E)
    const ctxAttr = document.getElementById('chartAttributesRate')?.getContext('2d');
    if (ctxAttr) {
        if (attributeChart) attributeChart.destroy();
        attributeChart = new Chart(ctxAttr, {
            type: 'bar',
            data: {
                labels: ['A (Len≥8)', 'B (Upper)', 'C (Lower)', 'D (Digit)', 'E (Symbol)'],
                datasets: [{
                    label: 'Fulfillment Rate (%)',
                    data: [
                        data.attributes_rate.A,
                        data.attributes_rate.B,
                        data.attributes_rate.C,
                        data.attributes_rate.D,
                        data.attributes_rate.E
                    ],
                    backgroundColor: 'rgba(0, 242, 254, 0.7)',
                    borderColor: '#00f2fe',
                    borderWidth: 1,
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { max: 100, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { display: false } }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
}
