document.addEventListener('DOMContentLoaded', function() {
    const yearSelect = document.getElementById('year-select');
    const monthSelect = document.getElementById('month-select');
    const paisSelect = document.getElementById('pais-select');
    const produtoFilter = document.getElementById('produto-filter');
    const applyButton = document.getElementById('apply-filters');
    const loadingOverlay = document.getElementById('loading-overlay');

    // Carrega lista de países
    loadPaises();

    // Event listeners
    console.log('Registrando event listeners...');
    yearSelect.addEventListener('change', () => {
        console.log('Ano mudou');
        loadPaises();
    });
    monthSelect.addEventListener('change', () => {
        console.log('Mês mudou');
        loadPaises();
    });
    paisSelect.addEventListener('change', () => {
        console.log('País mudou para:', paisSelect.value);
        loadProdutos();
    });
    applyButton.addEventListener('click', loadAnaliseData);

    function loadPaises() {
        const year = yearSelect.value;
        const month = monthSelect.value;

        showLoading();

        fetch(`/api/paises?year=${year}&month=${month}`)
            .then(response => response.json())
            .then(data => {
                paisSelect.innerHTML = '<option value="">Selecione um país</option>';
                
                if (data.paises && data.paises.length > 0) {
                    data.paises.forEach(pais => {
                        const option = document.createElement('option');
                        option.value = pais;
                        option.textContent = pais;
                        paisSelect.appendChild(option);
                    });
                }
                
                // Limpa produtos quando recarregar países
                produtoFilter.innerHTML = '<option value="">Selecione um país primeiro</option>';
                
                hideLoading();
            })
            .catch(error => {
                console.error('Erro ao carregar países:', error);
                hideLoading();
                alert('Erro ao carregar lista de países');
            });
    }

    function loadProdutos() {
        const year = yearSelect.value;
        const month = monthSelect.value;
        const pais = paisSelect.value;

        console.log('loadProdutos chamado:', { year, month, pais });

        if (!pais) {
            produtoFilter.innerHTML = '<option value="">Selecione um país primeiro</option>';
            return;
        }

        produtoFilter.innerHTML = '<option value="">Carregando...</option>';

        const url = `/api/produtos-pais?year=${year}&month=${month}&pais=${encodeURIComponent(pais)}`;
        console.log('Buscando produtos:', url);

        fetch(url)
            .then(response => response.json())
            .then(data => {
                console.log('Produtos recebidos:', data);
                produtoFilter.innerHTML = '<option value="">Todos os produtos</option>';
                
                if (data.produtos && data.produtos.length > 0) {
                    console.log(`Adicionando ${data.produtos.length} produtos`);
                    data.produtos.forEach(produto => {
                        const option = document.createElement('option');
                        option.value = produto;
                        option.textContent = produto;
                        produtoFilter.appendChild(option);
                    });
                } else {
                    console.log('Nenhum produto encontrado');
                }
            })
            .catch(error => {
                console.error('Erro ao carregar produtos:', error);
                produtoFilter.innerHTML = '<option value="">Erro ao carregar</option>';
            });
    }

    function loadAnaliseData() {
        const year = yearSelect.value;
        const month = monthSelect.value;
        const pais = paisSelect.value;
        const produto = produtoFilter.value.trim();

        if (!pais) {
            alert('Por favor, selecione um país');
            return;
        }

        showLoading();

        let url = `/api/analise-pais-data?year=${year}&month=${month}&pais=${encodeURIComponent(pais)}`;
        if (produto) {
            url += `&produto=${encodeURIComponent(produto)}`;
        }

        fetch(url)
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
                alert('Erro ao carregar dados. Tente novamente.');
            });
    }

    function updateKPIs(kpis) {
        document.getElementById('kpi-total-fob').textContent = 
            formatCurrency(kpis.total_fob);
        
        document.getElementById('kpi-total-peso').textContent = 
            formatWeight(kpis.total_peso_kg);
        
        document.getElementById('kpi-produtos').textContent = 
            kpis.num_produtos.toLocaleString('pt-BR');
        
        document.getElementById('kpi-preco-medio').textContent = 
            'US$ ' + kpis.preco_medio_kg.toFixed(2);
    }

    function renderCharts(charts) {
        if (charts.bubble_chart) {
            const bubbleData = JSON.parse(charts.bubble_chart);
            Plotly.newPlot('bubble-chart', bubbleData.data, bubbleData.layout, {
                responsive: true,
                displayModeBar: true
            });
        }

        if (charts.bar_chart) {
            const barData = JSON.parse(charts.bar_chart);
            Plotly.newPlot('bar-chart', barData.data, barData.layout, {
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

    window.addEventListener('resize', function() {
        Plotly.Plots.resize('bubble-chart');
        Plotly.Plots.resize('bar-chart');
    });
});
