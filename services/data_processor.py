import pandas as pd
from typing import Dict, List

class DataProcessor:
    """Processamento e agregação de dados de exportação"""
    
    def aggregate_by_ncm(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """Agrega dados por NCM (produto)"""
        if df.empty:
            return pd.DataFrame()
        
        # Garante que descricao_ncm existe
        if 'descricao_ncm' not in df.columns:
            from .codigos_comexstat import get_ncm_descricao
            df['descricao_ncm'] = df['ncm'].apply(lambda x: get_ncm_descricao(str(x)))
        
        # Agrega por NCM e descrição
        agg = df.groupby(['ncm', 'descricao_ncm']).agg({
            'valor_fob': 'sum',
            'peso_kg': 'sum'
        }).reset_index()
        
        agg = agg.sort_values('valor_fob', ascending=False)
        return agg.head(top_n)
    
    def aggregate_by_country(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """Agrega dados por país de destino"""
        if df.empty or 'pais' not in df.columns:
            return pd.DataFrame()
        
        agg = df.groupby('pais').agg({
            'valor_fob': 'sum',
            'peso_kg': 'sum'
        }).reset_index()
        
        agg = agg.sort_values('valor_fob', ascending=False)
        return agg.head(top_n)
    
    def aggregate_by_transport(self, df: pd.DataFrame) -> pd.DataFrame:
        """Agrega dados por modal de transporte"""
        if df.empty or 'via' not in df.columns:
            return pd.DataFrame()
        
        agg = df.groupby('via').agg({
            'valor_fob': 'sum',
            'peso_kg': 'sum'
        }).reset_index()
        
        agg = agg.sort_values('valor_fob', ascending=False)
        return agg
    
    def aggregate_by_state(self, df: pd.DataFrame) -> pd.DataFrame:
        """Agrega dados por estado (UF)"""
        if df.empty or 'uf' not in df.columns:
            return pd.DataFrame()
        
        agg = df.groupby('uf').agg({
            'valor_fob': 'sum',
            'peso_kg': 'sum'
        }).reset_index()
        
        agg = agg.sort_values('valor_fob', ascending=False)
        return agg
    
    def calculate_growth(self, current: pd.DataFrame, previous: pd.DataFrame, 
                        group_by: str, value_col: str = 'valor_fob') -> pd.DataFrame:
        """Calcula crescimento entre dois períodos"""
        if current.empty or previous.empty:
            return pd.DataFrame()
        
        current_agg = current.groupby(group_by)[value_col].sum()
        previous_agg = previous.groupby(group_by)[value_col].sum()
        
        growth = pd.DataFrame({
            'current': current_agg,
            'previous': previous_agg
        }).fillna(0)
        
        growth['growth_pct'] = ((growth['current'] - growth['previous']) / 
                                growth['previous'] * 100)
        growth['growth_pct'] = growth['growth_pct'].replace([float('inf'), float('-inf')], 0)
        
        return growth.reset_index()
    
    def apply_filters(self, df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
        """Aplica filtros dinâmicos ao dataframe"""
        filtered = df.copy()
        
        if 'ncm' in filters and filters['ncm']:
            filtered = filtered[filtered['ncm'].isin(filters['ncm'])]
        
        if 'pais' in filters and filters['pais']:
            filtered = filtered[filtered['pais'].isin(filters['pais'])]
        
        if 'uf' in filters and filters['uf']:
            filtered = filtered[filtered['uf'].isin(filters['uf'])]
        
        if 'via' in filters and filters['via']:
            filtered = filtered[filtered['via'].isin(filters['via'])]
        
        if 'min_fob' in filters:
            filtered = filtered[filtered['valor_fob'] >= filters['min_fob']]
        
        if 'max_fob' in filters:
            filtered = filtered[filtered['valor_fob'] <= filters['max_fob']]
        
        return filtered
    
    def format_currency(self, value: float) -> str:
        """Formata valores em moeda"""
        if value >= 1_000_000_000:
            return f"${value/1_000_000_000:.2f}B"
        elif value >= 1_000_000:
            return f"${value/1_000_000:.2f}M"
        elif value >= 1_000:
            return f"${value/1_000:.2f}K"
        return f"${value:.2f}"
    
    def format_weight(self, value: float) -> str:
        """Formata peso em unidades apropriadas"""
        if value >= 1_000_000:
            return f"{value/1_000_000:.2f}K ton"
        elif value >= 1_000:
            return f"{value/1_000:.2f} ton"
        return f"{value:.2f} kg"    
    def process_time_series(self, df: pd.DataFrame, agregacao: str = 'mensal') -> Dict:
        """
        Processa dados para análise de séries temporais com desagregação por NCM
        
        Args:
            df: DataFrame com dados de exportação (com colunas ano, mes)
            agregacao: 'mensal', 'trimestral' ou 'anual'
        
        Returns:
            Dict com séries temporais desagregadas por NCM e país
        """
        if df.empty:
            return {}
        
        # Garante descrição NCM
        if 'descricao_ncm' not in df.columns:
            from .codigos_comexstat import get_ncm_descricao
            df['descricao_ncm'] = df['ncm'].apply(lambda x: get_ncm_descricao(str(x)))
        
        # Cria coluna de data
        df['data'] = pd.to_datetime(df['ano'].astype(str) + '-' + df['mes'].astype(str).str.zfill(2) + '-01')
        
        # Agregação conforme solicitado
        if agregacao == 'trimestral':
            df['periodo'] = df['data'].dt.to_period('Q')
        elif agregacao == 'anual':
            df['periodo'] = df['data'].dt.to_period('Y')
        else:  # mensal
            df['periodo'] = df['data'].dt.to_period('M')
        
        # Série temporal total (agregado geral)
        total_series = df.groupby('periodo').agg({
            'valor_fob': 'sum',
            'peso_kg': 'sum',
            'quantidade': 'sum' if 'quantidade' in df.columns else lambda x: 0
        }).reset_index()
        total_series['periodo_str'] = total_series['periodo'].astype(str)
        
        # Garante que quantidade existe
        if 'quantidade' not in total_series.columns:
            total_series['quantidade'] = 0
        
        # Identifica top 5 NCMs por valor total
        top_ncms = df.groupby(['ncm', 'descricao_ncm'])['valor_fob'].sum().nlargest(5).reset_index()
        
        # Séries individuais por NCM (desagregadas)
        ncm_series_list = []
        for _, ncm_row in top_ncms.iterrows():
            ncm_code = ncm_row['ncm']
            ncm_desc = ncm_row['descricao_ncm']
            
            ncm_df_filtered = df[df['ncm'] == ncm_code]
            
            agg_dict = {
                'valor_fob': 'sum',
                'peso_kg': 'sum'
            }
            if 'quantidade' in ncm_df_filtered.columns:
                agg_dict['quantidade'] = 'sum'
            
            ncm_data = ncm_df_filtered.groupby('periodo').agg(agg_dict).reset_index()
            
            ncm_data['periodo_str'] = ncm_data['periodo'].astype(str)
            ncm_data['ncm'] = ncm_code
            ncm_data['descricao_ncm'] = ncm_desc
            
            # Calcula preço médio implícito (FOB / quantidade)
            if 'quantidade' in ncm_data.columns and ncm_data['quantidade'].sum() > 0:
                ncm_data['preco_medio'] = ncm_data['valor_fob'] / ncm_data['quantidade']
                ncm_data['preco_medio'] = ncm_data['preco_medio'].replace([float('inf'), float('-inf')], 0).fillna(0)
            else:
                ncm_data['preco_medio'] = 0
            
            ncm_series_list.append(ncm_data)
        
        # Top 5 países por NCM (desagregado)
        ncm_pais_series_list = []
        for _, ncm_row in top_ncms.iterrows():
            ncm_code = ncm_row['ncm']
            ncm_desc = ncm_row['descricao_ncm']
            
            # Filtra dados deste NCM
            ncm_df = df[df['ncm'] == ncm_code]
            
            # Identifica top 5 países para este NCM
            top_paises_ncm = ncm_df.groupby('pais')['valor_fob'].sum().nlargest(5).index.tolist()
            
            # Séries temporais por país para este NCM
            agg_dict = {
                'valor_fob': 'sum',
                'peso_kg': 'sum'
            }
            if 'quantidade' in ncm_df.columns:
                agg_dict['quantidade'] = 'sum'
            
            paises_ncm_data = ncm_df[ncm_df['pais'].isin(top_paises_ncm)].groupby(['periodo', 'pais']).agg(agg_dict).reset_index()
            
            paises_ncm_data['periodo_str'] = paises_ncm_data['periodo'].astype(str)
            paises_ncm_data['ncm'] = ncm_code
            paises_ncm_data['descricao_ncm'] = ncm_desc
            
            # Calcula share percentual de cada país no período
            total_por_periodo = paises_ncm_data.groupby('periodo')['valor_fob'].transform('sum')
            paises_ncm_data['share_pct'] = (paises_ncm_data['valor_fob'] / total_por_periodo * 100).round(2)
            
            ncm_pais_series_list.append(paises_ncm_data)
        
        # Agrupa top 5 países geral (todos os NCMs)
        top_paises_geral = df.groupby('pais')['valor_fob'].sum().nlargest(5).index.tolist()
        paises_series = df[df['pais'].isin(top_paises_geral)].groupby(['periodo', 'pais']).agg({
            'valor_fob': 'sum',
            'peso_kg': 'sum'
        }).reset_index()
        paises_series['periodo_str'] = paises_series['periodo'].astype(str)
        
        # Converte tipos numpy para Python nativos para serialização JSON
        def convert_to_native_types(df_list):
            result = []
            for item in df_list:
                if isinstance(item, pd.DataFrame):
                    # Converte int64, float64 para int, float
                    for col in item.select_dtypes(include=['int64', 'int32']).columns:
                        item[col] = item[col].astype(int)
                    for col in item.select_dtypes(include=['float64', 'float32']).columns:
                        item[col] = item[col].astype(float)
                result.append(item)
            return result
        
        ncm_series_list = convert_to_native_types(ncm_series_list)
        ncm_pais_series_list = convert_to_native_types(ncm_pais_series_list)
        
        # Converte top_ncms para tipos nativos
        top_ncms_native = []
        for record in top_ncms.to_dict('records'):
            native_record = {}
            for key, value in record.items():
                if pd.api.types.is_integer(value):
                    native_record[key] = int(value)
                elif pd.api.types.is_float(value):
                    native_record[key] = float(value)
                else:
                    native_record[key] = str(value)
            top_ncms_native.append(native_record)
        
        return {
            'total': total_series,
            'volume': total_series[['periodo_str', 'peso_kg']].copy(),
            'top_paises': paises_series,
            'ncm_series': ncm_series_list,  # Lista de séries individuais por NCM
            'ncm_pais_series': ncm_pais_series_list,  # Lista de séries país x NCM
            'top_ncms_info': top_ncms_native  # Info dos top NCMs (tipos nativos)
        }