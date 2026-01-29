import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict

class ChartGenerator:
    """Geração de visualizações interativas com Plotly"""
    
    def __init__(self):
        self.default_layout = {
            'template': 'plotly_white',
            'font': {'family': 'JetBrains Mono, monospace', 'size': 12},
            'margin': {'l': 50, 'r': 50, 't': 50, 'b': 50},
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
    
    def create_treemap(self, df: pd.DataFrame, labels_col: str, values_col: str, title: str) -> Dict:
        """Cria gráfico treemap"""
        if df.empty:
            return self._empty_chart(title)
        
        df = df.copy()
        
        fig = go.Figure(go.Treemap(
            labels=df[labels_col].tolist(),
            parents=[""] * len(df),
            values=df[values_col].tolist(),
            textposition='middle center',
            textfont={'size': 14},
            marker=dict(
                colorscale='Blues',
                line=dict(width=2, color='white')
            ),
            hovertemplate='<b>%{label}</b><br>Valor: $%{value:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            **self.default_layout,
            title={'text': title, 'x': 0.5, 'xanchor': 'center'},
            height=500
        )
        
        return fig.to_dict()
    
    def create_bar_chart(self, df: pd.DataFrame, x_col: str, y_col: str, 
                        title: str, horizontal: bool = True) -> Dict:
        """Cria gráfico de barras"""
        if df.empty:
            return self._empty_chart(title)
        
        # Formata valores para exibição
        df = df.copy()
        df['formatted_value'] = df[y_col].apply(lambda x: f"${x:,.2f}")
        
        # Encurta nomes dos produtos
        def shorten_name(name):
            replacements = {
                'Café não torrado, não descafeinado': 'Café',
                'Outros açúcares de cana': 'Açúcar',
                'Petróleo bruto': 'Petróleo',
                'Minério de ferro': 'Minério Fe',
                'Milho, exceto para semeadura': 'Milho',
                'Sementes de soja': 'Soja',
                'Pasta química de madeira': 'Celulose',
                'Carne bovina desossada, congelada': 'Carne bovina',
                'Algodão, não cardado nem penteado': 'Algodão',
                'Tabaco parcialmente destalado': 'Tabaco',
                'Ferronióbio': 'Ferronióbio',
                'Tortas e outros resíduos sólidos da extração do óleo de soja': 'Farelo soja',
                'Pedaços e miudezas comestíveis de galos e galinhas da espécie doméstica, congelados': 'Frango (pedaços)',
                'para dissolução': '(dissolução)',
                'Minério de ferro e seus concentrados': 'Minério Fe',
                'não aglomerados': ''
            }
            
            short = name
            for long, replace in replacements.items():
                if long.lower() in short.lower():
                    short = short.replace(long, replace)
            
            # Remove textos extras comuns
            short = short.replace(', não aglomerados', '')
            short = short.replace(', exceto para semeadura', '')
            short = short.strip(', ')
            
            if len(short) > 45:
                return short[:42] + '...'
            return short
        
        df['short_label'] = df[x_col].apply(shorten_name)
        
        if horizontal:
            fig = go.Figure(go.Bar(
                y=df['short_label'],
                x=df[y_col],
                orientation='h',
                text=df['formatted_value'],
                textposition='outside',
                marker=dict(
                    color='#0056A3',
                    line=dict(color='#003B5C', width=1)
                ),
                hovertemplate='<b>%{y}</b><br>Valor: %{text}<extra></extra>'
            ))
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title='Valor FOB (USD)',
                yaxis_title=''
            )
        else:
            fig = go.Figure(go.Bar(
                x=df[x_col],
                y=df[y_col],
                text=df['formatted_value'],
                textposition='outside',
                marker_color='#1f77b4'
            ))
            fig.update_layout(
                xaxis_title='',
                yaxis_title='Valor FOB (USD)'
            )
        
        fig.update_layout(
            title=title,
            **self.default_layout
        )
        
        return fig.to_json()
    
    def create_pie_chart(self, df: pd.DataFrame, labels_col: str, 
                        values_col: str, title: str) -> Dict:
        """Cria gráfico de pizza com nomes encurtados"""
        if df.empty:
            return self._empty_chart(title)
        
        df = df.copy()
        
        # Função para encurtar nomes longos
        def shorten_name(name):
            # Remover detalhes desnecessários - mais agressivo
            replacements = {
                'Café não torrado, não descafeinado': 'Café',
                'Outros açúcares de cana': 'Açúcar de cana',
                'Petróleo bruto': 'Petróleo',
                'Minério de ferro': 'Minério Fe',
                'Milho, exceto para semeadura': 'Milho',
                'Sementes de soja': 'Soja',
                'Pasta química de madeira': 'Celulose',
                'Carne bovina desossada, congelada': 'Carne bovina',
                'Algodão, não cardado nem penteado': 'Algodão',
                'Tortas e outros resíduos sólidos da extração do óleo de soja': 'Farelo soja',
                'Tabaco parcialmente destalado': 'Tabaco',
                'Ferronióbio': 'Ferronióbio'
            }
            
            short = name
            for long, replace in replacements.items():
                if long.lower() in short.lower():
                    short = replace
                    break
            
            # Limpa textos extras comuns
            short = short.replace(', não aglomerados', '')
            short = short.replace(', exceto para semeadura', '')
            short = short.replace('Pedaços e miudezas comestíveis de galos e galinhas da espécie doméstica, congelados', 'Frango')
            short = short.replace('para dissolução', '')
            short = short.strip(', ')
            
            # Limite mais agressivo
            if len(short) > 25:
                return short[:22] + '...'
            return short
        
        df['short_labels'] = df[labels_col].apply(shorten_name)
        
        # Paleta de cores corporativa
        colors = ['#003B5C', '#0056A3', '#0068A7', '#0077C0', '#0086D9', 
                  '#FF8C00', '#FF9519', '#FFA74B', '#FFB064', '#8B95A5']
        
        fig = go.Figure(go.Pie(
            labels=df['short_labels'],
            values=df[values_col],
            hole=0.4,
            textinfo='percent',
            textposition='inside',
            textfont=dict(size=12, color='white', family='JetBrains Mono', weight='bold'),
            marker=dict(
                colors=colors,
                line=dict(color='white', width=2)
            ),
            hovertemplate='<b>%{label}</b><br>Valor: $%{value:,.0f}<br>%{percent}<extra></extra>',
            showlegend=True
        ))
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=16, family='JetBrains Mono')
            ),
            font=dict(family='JetBrains Mono', size=11),
            legend=dict(
                orientation='v',
                yanchor='middle',
                y=0.5,
                xanchor='left',
                x=1.02,
                font=dict(size=10)
            ),
            margin={'l': 20, 'r': 150, 't': 60, 'b': 20},
            height=550
        )
        
        return fig.to_json()
    
    def create_line_chart(self, df: pd.DataFrame, x_col: str, y_col: str,
                         title: str, group_col: str = None) -> Dict:
        """Cria gráfico de linha"""
        if df.empty:
            return self._empty_chart(title)
        
        if group_col:
            fig = px.line(df, x=x_col, y=y_col, color=group_col, 
                         markers=True)
        else:
            fig = go.Figure(go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode='lines+markers',
                line=dict(color='#0056A3', width=3),
                marker=dict(size=8, color='#FF8C00'),
                fill='tozeroy',
                fillcolor='rgba(0, 86, 163, 0.1)'
            ))
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=16, family='JetBrains Mono')
            ),
            xaxis_title=x_col,
            yaxis_title=y_col,
            font=dict(family='JetBrains Mono', size=12),
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig.to_json()
    
    def create_brazil_map(self, df: pd.DataFrame, title: str) -> Dict:
        """Cria mapa do Brasil com dados por estado"""
        if df.empty:
            return self._empty_chart(title)
        
        # Mapeamento de UF para nomes completos
        uf_names = {
            'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
            'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal',
            'ES': 'Espírito Santo', 'GO': 'Goiás', 'MA': 'Maranhão',
            'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul', 'MG': 'Minas Gerais',
            'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná', 'PE': 'Pernambuco',
            'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
            'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima',
            'SC': 'Santa Catarina', 'SP': 'São Paulo', 'SE': 'Sergipe',
            'TO': 'Tocantins'
        }
        
        # Coordenadas geográficas aproximadas dos estados (centro do estado)
        state_coords = {
            'AC': [-9.0238, -70.8120], 'AL': [-9.5713, -36.7820], 'AP': [1.4129, -51.7774],
            'AM': [-3.4168, -65.8561], 'BA': [-12.5797, -41.7007], 'CE': [-5.4984, -39.3206],
            'DF': [-15.7998, -47.8645], 'ES': [-19.1834, -40.3089], 'GO': [-15.8270, -49.8362],
            'MA': [-4.9609, -45.2744], 'MT': [-12.6819, -56.9211], 'MS': [-20.7722, -54.7852],
            'MG': [-18.5122, -44.5550], 'PA': [-1.9981, -54.9306], 'PB': [-7.2400, -36.7820],
            'PR': [-24.8932, -51.4309], 'PE': [-8.8137, -36.9541], 'PI': [-7.7183, -42.7289],
            'RJ': [-22.9099, -43.2095], 'RN': [-5.4026, -36.9541], 'RS': [-30.0346, -51.2177],
            'RO': [-11.5057, -63.5806], 'RR': [2.7376, -62.0751], 'SC': [-27.2423, -50.2189],
            'SP': [-23.5505, -46.6333], 'SE': [-10.5741, -37.3857], 'TO': [-10.1753, -48.2982]
        }
        
        df = df.copy()
        df['estado'] = df['uf'].map(uf_names)
        df['lat'] = df['uf'].map(lambda x: state_coords.get(x, [0, 0])[0])
        df['lon'] = df['uf'].map(lambda x: state_coords.get(x, [0, 0])[1])
        df['valor_formatado'] = df['valor_fob'].apply(lambda x: f"US$ {x:,.2f}")
        df['peso_formatado'] = df['peso_kg'].apply(lambda x: f"{x:,.0f} kg")
        
        # Cria mapa de bolhas sobre o Brasil
        fig = go.Figure()
        
        # Adiciona os estados como bolhas
        fig.add_trace(go.Scattergeo(
            lon=df['lon'],
            lat=df['lat'],
            text=df['estado'],
            mode='markers',
            marker=dict(
                size=df['valor_fob'],
                sizemode='area',
                sizeref=2.*max(df['valor_fob'])/(50.**2),
                sizemin=5,
                color=df['valor_fob'],
                colorscale='Blues',
                showscale=True,
                colorbar=dict(title="Valor FOB<br>(USD)", thickness=15),
                line=dict(width=0.5, color='white')
            ),
            hovertemplate='<b>%{text}</b><br>' +
                         'Valor: ' + df['valor_formatado'] + '<br>' +
                         'Peso: ' + df['peso_formatado'] +
                         '<extra></extra>'
        ))
        
        # Configura o mapa para focar no Brasil
        fig.update_geos(
            center=dict(lon=-52, lat=-15),
            projection_scale=3.5,
            visible=True,
            resolution=50,
            showcountries=True,
            countrycolor="lightgray",
            showland=True,
            landcolor="rgb(250, 250, 250)",
            showlakes=True,
            lakecolor="rgb(230, 240, 255)",
            showcoastlines=True,
            coastlinecolor="gray"
        )
        
        fig.update_layout(
            title=title,
            geo=dict(
                scope='south america',
                projection_type='natural earth'
            ),
            **self.default_layout
        )
        
        return fig.to_json()
    
    def create_bubble_chart(self, df: pd.DataFrame, x_col: str, y_col: str, 
                           size_col: str, text_col: str, title: str) -> Dict:
        """Cria gráfico de dispersão de bolhas melhorado com escala logarítmica"""
        if df.empty:
            return self._empty_chart(title)
        
        df = df.copy()
        
        # Função para encurtar nomes
        def shorten_name(name):
            replacements = {
                'Café não torrado, não descafeinado': 'Café',
                'Outros açúcares de cana': 'Açúcar',
                'Petróleo bruto': 'Petróleo',
                'Minério de ferro': 'Minério Fe',
                'Milho, exceto para semeadura': 'Milho',
                'Sementes de soja': 'Soja',
                'Pasta química de madeira': 'Celulose',
                'Carne bovina desossada, congelada': 'Carne bovina',
                'Algodão, não cardado nem penteado': 'Algodão',
                'Tabaco parcialmente destalado': 'Tabaco',
                'Ferronióbio': 'Ferronióbio',
                'Tortas e outros resíduos sólidos da extração do óleo de soja': 'Farelo soja'
            }
            
            for long, short in replacements.items():
                if long.lower() in name.lower():
                    return short
            
            if len(name) > 30:
                return name[:27] + '...'
            return name
        
        df['short_name'] = df[text_col].apply(shorten_name)
        
        # DEBUG: Print dos valores para verificar
        import numpy as np
        print("\n=== DEBUG BUBBLE CHART ===")
        print(f"Coluna de tamanho: {size_col}")
        print(f"Valores originais:\n{df[[text_col, size_col]].head(10)}")
        print(f"Min: {df[size_col].min():,.0f}, Max: {df[size_col].max():,.0f}")
        
        # NORMALIZAÇÃO LINEAR DIRETA - mais agressiva
        min_size = 8
        max_size = 100
        values = df[size_col].values
        
        # Proteção contra divisão por zero
        if values.max() == values.min():
            df['bubble_size'] = 30  # tamanho fixo se todos iguais
            print("AVISO: Todos valores são iguais!")
        else:
            # Normalização LINEAR pura (mais agressiva que raiz quadrada)
            normalized = (values - values.min()) / (values.max() - values.min())
            df['bubble_size'] = normalized * (max_size - min_size) + min_size
            print(f"Tamanhos calculados:\n{df[['short_name', 'bubble_size']].head(10)}")
        
        # Paleta de cores corporativa
        colors = ['#003B5C', '#0056A3', '#0068A7', '#0077C0', '#0086D9', 
                  '#FF8C00', '#FF9519', '#FFA74B', '#FFB064', '#8B95A5',
                  '#0095D9', '#FFC04B', '#7A8896', '#60B8FF', '#FFD54F']
        
        df['color'] = [colors[i % len(colors)] for i in range(len(df))]
        
        fig = go.Figure()
        
        # Adiciona cada produto como trace separado
        for idx, row in df.iterrows():
            # DEBUG: confirma o tamanho usado
            bubble_size_final = float(row['bubble_size']) if not pd.isna(row['bubble_size']) else 30
            
            fig.add_trace(go.Scatter(
                x=[row[x_col]],
                y=[row[y_col]],
                mode='markers',
                marker=dict(
                    size=bubble_size_final,
                    color=row['color'],
                    line=dict(width=2, color='white'),
                    opacity=0.85
                ),
                name=row['short_name'],
                hovertemplate=(
                    f"<b>{row['short_name']}</b><br>" +
                    f"Peso: {row[x_col]:,.0f} kg<br>" +
                    f"Preço: US$ {row[y_col]:,.2f}/kg<br>" +
                    f"Valor: ${row[size_col]:,.0f}<br>" +
                    f"Tamanho bolha: {bubble_size_final:.1f}px<br>" +
                    "<extra></extra>"
                ),
                showlegend=True
            ))
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=16, family='JetBrains Mono')
            ),
            xaxis=dict(
                title='Peso (kg)',
                type='log',  # Escala logarítmica para melhor distribuição
                gridcolor='#E8EEF2',
                showgrid=True
            ),
            yaxis=dict(
                title='Preço Médio (USD/kg)',
                type='log',  # Escala logarítmica
                gridcolor='#E8EEF2',
                showgrid=True
            ),
            font=dict(family='JetBrains Mono', size=12),
            legend=dict(
                orientation='v',
                yanchor='top',
                y=1,
                xanchor='left',
                x=1.05,
                font=dict(size=10)
            ),
            hovermode='closest',
            margin={'l': 80, 'r': 200, 't': 60, 'b': 80},
            height=600,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig.to_json()
    
    def create_time_series_chart(self, df: pd.DataFrame, title: str, y_label: str) -> str:
        """Cria gráfico de linha para séries temporais"""
        if df.empty:
            return self._empty_chart(title)
        
        fig = go.Figure()
        
        if 'peso_kg' in df.columns:
            # Gráfico de volume
            fig.add_trace(go.Scatter(
                x=df['periodo_str'],
                y=df['peso_kg'],
                mode='lines+markers',
                name=y_label,
                line=dict(color='#2ecc71', width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{x}</b><br>' + y_label + ': %{y:,.0f}<extra></extra>'
            ))
        else:
            # Gráfico de valor
            fig.add_trace(go.Scatter(
                x=df['periodo_str'],
                y=df['valor_fob'],
                mode='lines+markers',
                name=y_label,
                line=dict(color='#3498db', width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{x}</b><br>' + y_label + ': US$ %{y:,.0f}<extra></extra>'
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Período',
            yaxis_title=y_label,
            hovermode='x unified',
            **self.default_layout,
            height=400
        )
        
        return fig.to_json()
    
    def create_multi_line_chart(self, df: pd.DataFrame, title: str, y_label: str) -> str:
        """Cria gráfico de múltiplas linhas para comparação temporal"""
        if df.empty:
            return self._empty_chart(title)
        
        fig = go.Figure()
        
        # Determina qual coluna usar para agrupar (pais ou descricao_ncm)
        if 'pais' in df.columns:
            group_col = 'pais'
        elif 'descricao_ncm' in df.columns:
            group_col = 'descricao_ncm'
        else:
            group_col = 'ncm'
        
        # Cores para as linhas
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
        
        # Adiciona uma linha para cada grupo
        for i, group in enumerate(df[group_col].unique()):
            group_data = df[df[group_col] == group]
            fig.add_trace(go.Scatter(
                x=group_data['periodo_str'],
                y=group_data['valor_fob'],
                mode='lines+markers',
                name=str(group)[:30],  # Limita nome a 30 caracteres
                line=dict(color=colors[i % len(colors)], width=2.5),
                marker=dict(size=6),
                hovertemplate='<b>' + str(group)[:30] + '</b><br>%{x}<br>Valor: US$ %{y:,.0f}<extra></extra>'
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Período',
            yaxis_title=y_label,
            hovermode='x unified',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            ),
            **self.default_layout,
            height=450
        )
        
        return fig.to_json()
    
    def _empty_chart(self, title: str) -> Dict:
        """Retorna gráfico vazio quando não há dados"""
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font={'size': 16}
        )
        fig.update_layout(
            title=title,
            **self.default_layout
        )
        return fig.to_json()
