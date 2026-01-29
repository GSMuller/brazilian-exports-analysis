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

        console.log('Carregando dados:', year, month);
        showLoading();

        fetch(`/api/dashboard-data?year=${year}&month=${month}&t=${Date.now()}`)
            .then(response => {
                console.log('Resposta recebida:', response.status);
                if (!response.ok) {
                    throw new Error('Erro ao carregar dados');
                }
                return response.json();
            })
            .then(data => {
                console.log('Dados recebidos:', data);
                updateKPIs(data.kpis);
                renderCharts(data.charts);
                hideLoading();
            })
            .catch(error => {
                console.error('Erro ao carregar dados:', error);
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
        
        // Atualiza cards de transporte mesmo se não houver dados
        if (kpis.transport_data && kpis.transport_data.length > 0) {
            updateTransportCards(kpis.transport_data);
        } else {
            // Se não houver dados, limpa os cards
            for (let i = 1; i <= 3; i++) {
                const card = document.getElementById(`transport-card-${i}`);
                if (card) {
                    const title = card.querySelector('.card-subtitle');
                    const value = card.querySelector('.card-title');
                    const percent = card.querySelector('.text-muted');
                    
                    if (title) title.textContent = '-';
                    if (value) value.textContent = '$0';
                    if (percent) percent.textContent = 'Sem dados';
                }
            }
        }
    }
    
    function updateTransportCards(transportData) {
        // Ordena por valor e pega top 3
        const sorted = transportData.sort((a, b) => b.valor - a.valor).slice(0, 3);
        
        // Garante que temos pelo menos 3 cards, preenche com "Sem dados"
        for (let i = 0; i < 3; i++) {
            const cardContainer = document.getElementById(`transport-card-${i + 1}`);
            if (cardContainer) {
                const title = cardContainer.querySelector('.card-subtitle');
                const value = cardContainer.querySelector('.card-title');
                const percent = cardContainer.querySelector('p.text-muted');
                
                if (sorted[i]) {
                    if (title) title.textContent = sorted[i].via;
                    if (value) value.textContent = formatCurrency(sorted[i].valor);
                    if (percent) percent.textContent = `${sorted[i].percentual.toFixed(2)}% do total`;
                } else {
                    if (title) title.textContent = '-';
                    if (value) value.textContent = '$0';
                    if (percent) percent.textContent = 'Sem dados';
                }
            }
        }
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

        // Renderiza gráfico de estados (mapa do Brasil)
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
        Plotly.Plots.resize('state-chart');
    });
});
