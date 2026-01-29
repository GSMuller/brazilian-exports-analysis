// Séries Temporais - Análise desagregada por NCM
let currentCharts = {};

document.addEventListener('DOMContentLoaded', function() {
    // Event listeners
    document.getElementById('agregacaoSelect').addEventListener('change', loadSeriesData);
    document.getElementById('aplicarFiltro').addEventListener('click', loadSeriesData);
    
    // Carrega dados iniciais
    loadSeriesData();
});

function loadSeriesData() {
    const anoInicio = document.getElementById('anoInicioSelect').value;
    const anoFim = document.getElementById('anoFimSelect').value;
    const agregacao = document.getElementById('agregacaoSelect').value;
    
    // Mostra loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('charts-container').style.display = 'none';
    
    fetch(`/api/series-temporais?ano_inicio=${anoInicio}&ano_fim=${anoFim}&agregacao=${agregacao}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Erro ao carregar dados: ' + data.error);
                return;
            }
            
            renderCharts(data);
            document.getElementById('loading').style.display = 'none';
            document.getElementById('charts-container').style.display = 'block';
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao carregar dados');
            document.getElementById('loading').style.display = 'none';
        });
}

function renderCharts(data) {
    // Limpa gráficos anteriores
    Object.values(currentCharts).forEach(chart => {
        if (chart && chart.destroy) chart.destroy();
    });
    currentCharts = {};
    
    // Gráfico de valor total agregado
    if (data.grafico_valor_total) {
        Plotly.newPlot('chart-valor-total', 
            JSON.parse(data.grafico_valor_total).data,
            JSON.parse(data.grafico_valor_total).layout,
            {responsive: true}
        );
    }
    
    // Gráfico de volume
    if (data.grafico_volume) {
        Plotly.newPlot('chart-volume', 
            JSON.parse(data.grafico_volume).data,
            JSON.parse(data.grafico_volume).layout,
            {responsive: true}
        );
    }
    
    // Gráfico de países
    if (data.grafico_paises_tempo) {
        Plotly.newPlot('chart-paises', 
            JSON.parse(data.grafico_paises_tempo).data,
            JSON.parse(data.grafico_paises_tempo).layout,
            {responsive: true}
        );
    }
    
    // Renderiza gráficos desagregados por NCM
    if (data.ncm_individual) {
        renderNCMCharts(data.ncm_individual, data.top_ncms);
    }
}

function renderNCMCharts(ncmData, topNCMs) {
    const container = document.getElementById('ncm-charts-container');
    container.innerHTML = ''; // Limpa container
    
    // Cria seção para cada NCM
    Object.keys(ncmData).forEach((ncmKey, index) => {
        const ncmInfo = ncmData[ncmKey];
        const ncmCode = ncmInfo.info.ncm;
        const ncmDesc = ncmInfo.info.descricao;
        
        // Cria card para este NCM
        const card = document.createElement('div');
        card.className = 'card mb-4';
        card.innerHTML = `
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">
                    <button class="btn btn-link text-white text-decoration-none w-100 text-start" 
                            type="button" 
                            data-bs-toggle="collapse" 
                            data-bs-target="#collapse-ncm-${ncmCode}">
                        ${ncmDesc} (NCM ${ncmCode})
                        <i class="fas fa-chevron-down float-end"></i>
                    </button>
                </h5>
            </div>
            <div id="collapse-ncm-${ncmCode}" class="collapse ${index === 0 ? 'show' : ''}">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <div id="ncm-valor-${ncmCode}" style="height: 400px;"></div>
                        </div>
                        <div class="col-md-6 mb-3">
                            <div id="ncm-preco-${ncmCode}" style="height: 400px;"></div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-12">
                            <div id="ncm-paises-${ncmCode}" style="height: 400px;"></div>
                        </div>
                    </div>
                    <div class="alert alert-info mt-3">
                        <strong>Análise Econômica:</strong>
                        <ul class="mb-0">
                            <li>Valor total mostra evolução das exportações deste produto específico</li>
                            <li>Preço médio indica se é commodity bruta (preço baixo) ou processada (preço alto)</li>
                            <li>Distribuição por países revela mudanças de parceiros comerciais</li>
                        </ul>
                    </div>
                </div>
            </div>
        `;
        
        container.appendChild(card);
        
        // Renderiza gráficos dentro do card
        if (ncmInfo.grafico_valor) {
            Plotly.newPlot(`ncm-valor-${ncmCode}`, 
                JSON.parse(ncmInfo.grafico_valor).data,
                JSON.parse(ncmInfo.grafico_valor).layout,
                {responsive: true}
            );
        }
        
        if (ncmInfo.grafico_preco_medio) {
            Plotly.newPlot(`ncm-preco-${ncmCode}`, 
                JSON.parse(ncmInfo.grafico_preco_medio).data,
                JSON.parse(ncmInfo.grafico_preco_medio).layout,
                {responsive: true}
            );
        }
        
        if (ncmInfo.grafico_paises) {
            Plotly.newPlot(`ncm-paises-${ncmCode}`, 
                JSON.parse(ncmInfo.grafico_paises).data,
                JSON.parse(ncmInfo.grafico_paises).layout,
                {responsive: true}
            );
        }
    });
}
