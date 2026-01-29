document.addEventListener('DOMContentLoaded', function() {
    const yearSelect = document.getElementById('year-select');
    const monthSelect = document.getElementById('month-select');
    const applyButton = document.getElementById('apply-filters');
    const loadingOverlay = document.getElementById('loading-overlay');

    // Carrega dados iniciais
    loadDashboardData();

    // Event listener para aplicar filtros
    applyButton.addEventListener('click', loadDashboardData);

    function loadDashboardData() {
        const year = yearSelect.value;
        const month = monthSelect.value;

        showLoading();

        fetch(`/api/dashboard-data?year=${year}&month=${month}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro ao carregar dados');
                }
                return response.json();
            })
            .then(data => {
                updateKPIs(data.kpis);
                renderCharts(data.charts);
                hideLoading();
            })
            .catch(error => {
                console.error('Erro:', error);
                hideLoading();
                alert('Erro ao carregar dados. Por favor, tente novamente.');
            });
    }

    function updateKPIs(kpis) {
        document.getElementById('kpi-total-fob').textContent = 
            formatCurrency(kpis.total_fob);
        
        document.getElementById('kpi-total-weight').textContent = 
            formatWeight(kpis.total_weight_kg);
        
        document.getElementById('kpi-countries').textContent = 
            kpis.num_countries.toLocaleString('pt-BR');
        
        document.getElementById('kpi-products').textContent = 
            kpis.num_products.toLocaleString('pt-BR');
    }

    function renderCharts(charts) {
        // Renderiza gráfico de NCM
        if (charts.ncm_chart) {
            const ncmData = JSON.parse(charts.ncm_chart);
            Plotly.newPlot('ncm-chart', ncmData.data, ncmData.layout, {
                responsive: true,
                displayModeBar: false
            });
        }

        // Renderiza gráfico de países
        if (charts.country_chart) {
            const countryData = JSON.parse(charts.country_chart);
            Plotly.newPlot('country-chart', countryData.data, countryData.layout, {
                responsive: true,
                displayModeBar: false
            });
        }

        // Renderiza gráfico de transporte
        if (charts.transport_chart) {
            const transportData = JSON.parse(charts.transport_chart);
            Plotly.newPlot('transport-chart', transportData.data, transportData.layout, {
                responsive: true,
                displayModeBar: false
            });
        }

        // Renderiza gráfico de estados
        if (charts.state_chart) {
            const stateData = JSON.parse(charts.state_chart);
            Plotly.newPlot('state-chart', stateData.data, stateData.layout, {
                responsive: true,
                displayModeBar: false
            });
        }
    }

    function formatCurrency(value) {
        if (value >= 1000000000) {
            return `$${(value / 1000000000).toFixed(2)}B`;
        } else if (value >= 1000000) {
            return `$${(value / 1000000).toFixed(2)}M`;
        } else if (value >= 1000) {
            return `$${(value / 1000).toFixed(2)}K`;
        }
        return `$${value.toFixed(2)}`;
    }

    function formatWeight(value) {
        if (value >= 1000000) {
            return `${(value / 1000000).toFixed(2)}M kg`;
        } else if (value >= 1000) {
            return `${(value / 1000).toFixed(2)}K kg`;
        }
        return `${value.toFixed(2)} kg`;
    }

    function showLoading() {
        loadingOverlay.classList.add('show');
    }

    function hideLoading() {
        loadingOverlay.classList.remove('show');
    }

    // Redimensiona gráficos quando a janela muda de tamanho
    window.addEventListener('resize', function() {
        Plotly.Plots.resize('ncm-chart');
        Plotly.Plots.resize('country-chart');
        Plotly.Plots.resize('transport-chart');
        Plotly.Plots.resize('state-chart');
    });
});
