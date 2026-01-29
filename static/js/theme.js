// ==================== PALETA DE CORES CORPORATIVA ====================
const CORPORATE_COLORS = {
    primary: '#003B5C',
    primaryLight: '#0056A3',
    secondary: '#8B95A5',
    accent: '#FF8C00',
    accentLight: '#FFA500',
    lightGray: '#E8EEF2',
    
    // Gradientes de azul
    blueGradient: ['#003B5C', '#004A75', '#00598E', '#0068A7', '#0077C0', '#0086D9'],
    
    // Gradientes de laranja
    orangeGradient: ['#FF8C00', '#FF9519', '#FF9E32', '#FFA74B', '#FFB064', '#FFB97D'],
    
    // Gradientes de cinza
    grayGradient: ['#5A6C7D', '#6B7C8D', '#7C8C9D', '#8B95A5', '#9BA5B5', '#ABB5C5']
};

// ==================== THEME MANAGER ====================
function initTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;
    
    // Carrega tema salvo
    const savedTheme = localStorage.getItem('theme') || 'light';
    htmlElement.setAttribute('data-theme', savedTheme);
    if (themeToggle) {
        themeToggle.checked = savedTheme === 'dark';
        
        // Event listener para toggle
        themeToggle.addEventListener('change', function() {
            const newTheme = this.checked ? 'dark' : 'light';
            htmlElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Dispara evento customizado para atualizar gráficos
            window.dispatchEvent(new Event('themeChanged'));
        });
    }
}

function getThemeColors() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    return {
        background: isDark ? '#1A1F2E' : '#FFFFFF',
        paper: isDark ? '#1A1F2E' : '#FFFFFF',
        text: isDark ? '#F0F3F7' : '#1A1A1A',
        textSecondary: isDark ? '#B8C5D6' : '#5A6C7D',
        gridColor: isDark ? '#2D3648' : '#E8EEF2',
        fontFamily: 'JetBrains Mono, monospace'
    };
}

// ==================== CHART THEME FUNCTIONS ====================
function applyThemeToChart(chartData, colorScheme = 'blueGradient', isMap = false) {
    const theme = getThemeColors();
    
    // Atualiza layout com tema
    if (!chartData.layout) chartData.layout = {};
    
    chartData.layout.paper_bgcolor = theme.background;
    chartData.layout.plot_bgcolor = theme.paper;
    chartData.layout.font = {
        family: theme.fontFamily,
        color: theme.text,
        size: 12
    };
    
    // Transições suaves
    chartData.layout.transition = {
        duration: 500,
        easing: 'cubic-in-out'
    };
    
    // Atualiza título
    if (chartData.layout.title) {
        if (typeof chartData.layout.title === 'string') {
            chartData.layout.title = {
                text: chartData.layout.title,
                font: {
                    family: theme.fontFamily,
                    color: theme.text,
                    size: 16,
                    weight: 600
                }
            };
        } else {
            chartData.layout.title.font = {
                family: theme.fontFamily,
                color: theme.text,
                size: 16,
                weight: 600
            };
        }
    }
    
    // Atualiza eixos
    if (chartData.layout.xaxis) {
        chartData.layout.xaxis.gridcolor = theme.gridColor;
        chartData.layout.xaxis.color = theme.textSecondary;
    }
    
    if (chartData.layout.yaxis) {
        chartData.layout.yaxis.gridcolor = theme.gridColor;
        chartData.layout.yaxis.color = theme.textSecondary;
    }
    
    // Atualiza cores dos dados
    if (chartData.data && chartData.data.length > 0) {
        chartData.data.forEach((trace, index) => {
            if (isMap) {
                // Para mapas, usa colorscale
                trace.colorscale = [
                    [0, CORPORATE_COLORS.lightGray],
                    [0.5, CORPORATE_COLORS.primaryLight],
                    [1, CORPORATE_COLORS.primary]
                ];
                if (trace.colorbar) {
                    trace.colorbar.tickfont = { color: theme.text };
                    if (trace.colorbar.title) {
                        trace.colorbar.title.font = { color: theme.text };
                    }
                }
            } else {
                // Para gráficos de barras/pizza/linha, usa cores do gradiente
                const colors = CORPORATE_COLORS[colorScheme];
                if (trace.type === 'bar') {
                    trace.marker = trace.marker || {};
                    trace.marker.color = colors;
                    trace.marker.line = {
                        color: theme.background,
                        width: 1.5
                    };
                } else if (trace.type === 'pie') {
                    trace.marker = trace.marker || {};
                    trace.marker.colors = colors;
                    trace.marker.line = {
                        color: theme.background,
                        width: 2
                    };
                } else if (trace.type === 'scatter') {
                    // Para gráficos de linha
                    trace.line = trace.line || {};
                    trace.line.color = colors[index % colors.length];
                    trace.line.width = 3;
                    trace.marker = trace.marker || {};
                    trace.marker.color = colors[index % colors.length];
                    // NÃO sobrescreve tamanho se já estiver definido (bubble chart)
                    if (!trace.marker.size) {
                        trace.marker.size = 6;
                    }
                }
            }
            
            // Atualiza hover
            if (trace.hovertemplate) {
                trace.hoverlabel = {
                    bgcolor: CORPORATE_COLORS.primary,
                    font: { color: '#FFFFFF', family: theme.fontFamily }
                };
            }
        });
    }
    
    return chartData;
}

function updatePlotlyChart(chartId, layoutUpdates = {}) {
    const chartElement = document.getElementById(chartId);
    if (chartElement && chartElement.data) {
        const theme = getThemeColors();
        const update = {
            paper_bgcolor: theme.background,
            plot_bgcolor: theme.paper,
            'font.color': theme.text,
            ...layoutUpdates
        };
        
        if (chartElement.layout && chartElement.layout.xaxis) {
            update['xaxis.gridcolor'] = theme.gridColor;
            update['xaxis.color'] = theme.textSecondary;
        }
        
        if (chartElement.layout && chartElement.layout.yaxis) {
            update['yaxis.gridcolor'] = theme.gridColor;
            update['yaxis.color'] = theme.textSecondary;
        }
        
        Plotly.relayout(chartId, update);
    }
}

// Inicializa tema ao carregar a página
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTheme);
} else {
    initTheme();
}
