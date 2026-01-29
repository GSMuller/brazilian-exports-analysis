from flask import Flask, render_template, jsonify, request
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Imports lazy - carrega apenas quando necessário
api_service = None
data_processor = None
chart_gen = None

def get_services():
    global api_service, data_processor, chart_gen
    if api_service is None:
        from services.api_service import ComexStatAPI
        from services.data_processor import DataProcessor
        from services.visualization import ChartGenerator
        api_service = ComexStatAPI()
        data_processor = DataProcessor()
        chart_gen = ChartGenerator()
    return api_service, data_processor, chart_gen

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analise-pais')
def analise_pais():
    return render_template('analise_pais.html')

@app.route('/series-temporais')
def series_temporais():
    return render_template('series_temporais.html')

@app.route('/api/dashboard-data')
def get_dashboard_data():
    """Retorna dados agregados para o dashboard principal"""
    try:
        api_service, data_processor, chart_gen = get_services()
        
        year = request.args.get('year', '2024')
        month = request.args.get('month', '12')
        
        # Busca dados da API
        raw_data = api_service.fetch_export_data(year, month)
        
        if raw_data.empty:
            return jsonify({'error': 'Nenhum dado encontrado'}), 404
        
        # Processa dados
        processed = data_processor.aggregate_by_ncm(raw_data)
        by_country = data_processor.aggregate_by_country(raw_data)
        by_transport = data_processor.aggregate_by_transport(raw_data)
        by_state = data_processor.aggregate_by_state(raw_data)
        
        # Gera visualizações
        charts = {
            'ncm_chart': chart_gen.create_pie_chart(
                processed.head(10), 
                'descricao_ncm' if 'descricao_ncm' in processed.columns else 'ncm', 
                'valor_fob',
                'Top 10 Produtos Exportados'
            ),
            'country_chart': chart_gen.create_bar_chart(
                by_country.head(10),
                'pais',
                'valor_fob',
                'Principais Destinos'
            ),
            'transport_chart': chart_gen.create_pie_chart(
                by_transport,
                'via',
                'valor_fob',
                'Distribuicao por Modal de Transporte'
            ),
            'state_chart': chart_gen.create_brazil_map(
                by_state,
                'Exportações por Estado'
            )
        }
        
        # Calcula KPIs
        total_fob = raw_data['valor_fob'].sum()
        total_weight = raw_data['peso_kg'].sum() if 'peso_kg' in raw_data.columns else 0
        num_countries = raw_data['pais'].nunique() if 'pais' in raw_data.columns else 0
        num_products = raw_data['ncm'].nunique() if 'ncm' in raw_data.columns else 0
        
        return jsonify({
            'kpis': {
                'total_fob': float(total_fob),
                'total_weight_kg': float(total_weight),
                'num_countries': int(num_countries),
                'num_products': int(num_products)
            },
            'charts': charts
        })
        
    except Exception as e:
        import traceback
        print(f"ERRO DETALHADO get_dashboard_data: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-data')
def get_export_data():
    """Endpoint para buscar dados brutos com filtros"""
    try:
        api_service, data_processor, chart_gen = get_services()
        
        year = request.args.get('year', '2024')
        month = request.args.get('month', '12')
        page = int(request.args.get('page', 1))
        
        data = api_service.fetch_export_data(year, month)
        
        # Paginação
        start = (page - 1) * app.config['ITEMS_PER_PAGE']
        end = start + app.config['ITEMS_PER_PAGE']
        
        paginated = data.iloc[start:end]
        
        return jsonify({
            'data': paginated.to_dict(orient='records'),
            'total': len(data),
            'page': page,
            'per_page': app.config['ITEMS_PER_PAGE']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/filters')
def get_available_filters():
    """Retorna filtros disponíveis"""
    return jsonify({
        'years': ['2024', '2023', '2022', '2021', '2020'],
        'months': [
            {'value': '01', 'label': 'Janeiro'},
            {'value': '02', 'label': 'Fevereiro'},
            {'value': '03', 'label': 'Marco'},
            {'value': '04', 'label': 'Abril'},
            {'value': '05', 'label': 'Maio'},
            {'value': '06', 'label': 'Junho'},
            {'value': '07', 'label': 'Julho'},
            {'value': '08', 'label': 'Agosto'},
            {'value': '09', 'label': 'Setembro'},
            {'value': '10', 'label': 'Outubro'},
            {'value': '11', 'label': 'Novembro'},
            {'value': '12', 'label': 'Dezembro'}
        ]
    })

@app.route('/api/paises')
def get_paises():
    """Retorna lista de países disponíveis"""
    try:
        api_service, data_processor, chart_gen = get_services()
        year = request.args.get('year', '2024')
        month = request.args.get('month', '12')
        
        raw_data = api_service.fetch_export_data(year, month)
        
        if 'pais' in raw_data.columns:
            paises = sorted(raw_data['pais'].unique().tolist())
            return jsonify({'paises': paises})
        
        return jsonify({'paises': []})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/produtos-pais')
def get_produtos_pais():
    """Retorna lista de produtos disponíveis para um país"""
    try:
        api_service, data_processor, chart_gen = get_services()
        year = request.args.get('year', '2024')
        month = request.args.get('month', '12')
        pais = request.args.get('pais')
        
        if not pais:
            return jsonify({'produtos': []})
        
        raw_data = api_service.fetch_export_data(year, month)
        dados_pais = raw_data[raw_data['pais'] == pais]
        
        if dados_pais.empty:
            return jsonify({'produtos': []})
        
        # Pega produtos únicos com descrição
        produtos = dados_pais[['descricao_ncm']].drop_duplicates()
        produtos_list = sorted(produtos['descricao_ncm'].tolist())
        
        return jsonify({'produtos': produtos_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analise-pais-data')
def get_analise_pais_data():
    """Retorna análise detalhada por país"""
    try:
        api_service, data_processor, chart_gen = get_services()
        
        year = request.args.get('year', '2024')
        month = request.args.get('month', '12')
        pais = request.args.get('pais')
        filtro_produto = request.args.get('produto', '').strip().lower()
        
        if not pais:
            return jsonify({'error': 'País não especificado'}), 400
        
        # Busca dados
        raw_data = api_service.fetch_export_data(year, month)
        
        # Filtra por país
        dados_pais = raw_data[raw_data['pais'] == pais]
        
        if dados_pais.empty:
            return jsonify({'error': f'Sem dados para {pais}'}), 404
        
        # Filtra por produto se especificado
        if filtro_produto:
            # Busca em NCM e descrição
            mask = (
                dados_pais['ncm'].astype(str).str.contains(filtro_produto, case=False, na=False) |
                dados_pais['descricao_ncm'].str.contains(filtro_produto, case=False, na=False)
            )
            dados_pais = dados_pais[mask]
            
            if dados_pais.empty:
                return jsonify({'error': f'Nenhum produto encontrado com "{filtro_produto}" para {pais}'}), 404
        
        # Agrega por produto
        produtos = dados_pais.groupby(['ncm', 'descricao_ncm'] if 'descricao_ncm' in dados_pais.columns else ['ncm']).agg({
            'valor_fob': 'sum',
            'peso_kg': 'sum'
        }).reset_index()
        
        produtos = produtos.sort_values('valor_fob', ascending=False)
        
        # Calcula métricas para o gráfico de bolhas
        produtos['preco_medio_kg'] = produtos['valor_fob'] / produtos['peso_kg']
        produtos['participacao'] = (produtos['valor_fob'] / produtos['valor_fob'].sum() * 100)
        
        # Top 20 produtos para não poluir o gráfico
        top_produtos = produtos.head(20)
        
        # Título dos gráficos
        titulo_base = f'{pais}'
        if filtro_produto:
            titulo_base += f' - "{filtro_produto}"'
        
        # Gráfico de bolhas
        bubble_chart = chart_gen.create_bubble_chart(
            top_produtos,
            'peso_kg',
            'preco_medio_kg',
            'valor_fob',
            'descricao_ncm' if 'descricao_ncm' in top_produtos.columns else 'ncm',
            f'Commodities Exportadas para {titulo_base}'
        )
        
        # Gráfico de barras top produtos
        bar_chart = chart_gen.create_bar_chart(
            top_produtos.head(10),
            'descricao_ncm' if 'descricao_ncm' in top_produtos.columns else 'ncm',
            'valor_fob',
            f'Top 10 Produtos - {titulo_base}'
        )
        
        # KPIs
        total_fob = dados_pais['valor_fob'].sum()
        total_peso = dados_pais['peso_kg'].sum()
        num_produtos = dados_pais['ncm'].nunique()
        preco_medio = total_fob / total_peso if total_peso > 0 else 0
        
        return jsonify({
            'kpis': {
                'total_fob': float(total_fob),
                'total_peso_kg': float(total_peso),
                'num_produtos': int(num_produtos),
                'preco_medio_kg': float(preco_medio)
            },
            'charts': {
                'bubble_chart': bubble_chart,
                'bar_chart': bar_chart
            }
        })
        
    except Exception as e:
        import traceback
        print(f"Erro na análise por país: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/series-temporais')
def get_series_temporais():
    """Retorna dados de séries temporais para análise temporal"""
    try:
        api_service, data_processor, chart_gen = get_services()
        
        ano_inicio = int(request.args.get('ano_inicio', '2020'))
        ano_fim = int(request.args.get('ano_fim', '2024'))
        agregacao = request.args.get('agregacao', 'mensal')
        ncm_selecionado = request.args.get('ncm', None)  # Filtro opcional por NCM específico
        
        # Busca dados para todos os anos/meses
        import pandas as pd
        all_data = []
        
        for year in range(ano_inicio, ano_fim + 1):
            for month in range(1, 13):
                df = api_service.fetch_export_data(str(year), str(month).zfill(2))
                if not df.empty:
                    all_data.append(df)
        
        if not all_data:
            return jsonify({'error': 'Nenhum dado encontrado para o período'}), 404
        
        # Combina todos os dados
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Filtra por NCM se especificado
        if ncm_selecionado:
            combined_df = combined_df[combined_df['ncm'] == ncm_selecionado]
        
        # Processa séries temporais com desagregação
        series_data = data_processor.process_time_series(combined_df, agregacao)
        
        # Se não há NCM específico, mostra análise geral + desagregação por top 5 NCMs
        if not ncm_selecionado:
            charts = {
                'grafico_valor_total': chart_gen.create_time_series_chart(
                    series_data['total'],
                    'Valor Total Exportado (Agregado)',
                    'Valor (US$ FOB)'
                ),
                'grafico_volume': chart_gen.create_time_series_chart(
                    series_data['volume'],
                    'Volume Total Exportado',
                    'Peso (Kg)'
                ),
                'grafico_paises_tempo': chart_gen.create_multi_line_chart(
                    series_data['top_paises'],
                    'Top 5 Países (Todos os Produtos)',
                    'Valor (US$ FOB)'
                ),
                'top_ncms': series_data.get('top_ncms_info', []),
                'ncm_individual': {}  # Gráficos individuais por NCM
            }
            
            # Adiciona gráficos individuais para cada top NCM
            for i, ncm_data in enumerate(series_data.get('ncm_series', [])):
                if ncm_data.empty:
                    continue
                    
                ncm_code = str(ncm_data['ncm'].iloc[0])
                ncm_desc = str(ncm_data['descricao_ncm'].iloc[0])
                
                charts['ncm_individual'][f'ncm_{ncm_code}'] = {
                    'info': {'ncm': ncm_code, 'descricao': ncm_desc},
                    'grafico_valor': chart_gen.create_time_series_chart(
                        ncm_data,
                        f'{ncm_desc} (NCM {ncm_code})',
                        'Valor (US$ FOB)'
                    ),
                    'grafico_preco_medio': chart_gen.create_time_series_chart(
                        ncm_data[['periodo_str', 'preco_medio']].rename(columns={'preco_medio': 'valor_fob'}),
                        f'Preço Médio - {ncm_desc}',
                        'Preço (US$/unidade)'
                    )
                }
                
                # Adiciona gráfico de países para este NCM
                if i < len(series_data.get('ncm_pais_series', [])):
                    pais_ncm_data = series_data['ncm_pais_series'][i]
                    charts['ncm_individual'][f'ncm_{ncm_code}']['grafico_paises'] = chart_gen.create_multi_line_chart(
                        pais_ncm_data,
                        f'Top 5 Países - {ncm_desc}',
                        'Valor (US$ FOB)'
                    )
        else:
            # Análise focada em um NCM específico
            charts = {
                'grafico_valor_total': chart_gen.create_time_series_chart(
                    series_data['total'],
                    f'Valor Exportado - NCM {ncm_selecionado}',
                    'Valor (US$ FOB)'
                ),
                'grafico_paises_tempo': chart_gen.create_multi_line_chart(
                    series_data['top_paises'],
                    f'Top 5 Países - NCM {ncm_selecionado}',
                    'Valor (US$ FOB)'
                )
            }
        
        return jsonify(charts)
        
    except Exception as e:
        import traceback
        print(f"Erro na série temporal: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("="*60)
    print("Servidor Flask - Dashboard de Exportacoes Brasileiras")
    print("Acesse: http://localhost:5000")
    print("Pressione CTRL+C para parar")
    print("="*60)
    app.run(debug=True, host='0.0.0.0', port=5000)
