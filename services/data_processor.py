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
        Processa dados para análise de séries temporais
        
        Args:
            df: DataFrame com dados de exportação (com colunas ano, mes)
            agregacao: 'mensal', 'trimestral' ou 'anual'
        
        Returns:
            Dict com séries temporais processadas
        """
        if df.empty:
            return {}
        
        # Cria coluna de data
        df['data'] = pd.to_datetime(df['ano'].astype(str) + '-' + df['mes'].astype(str).str.zfill(2) + '-01')
        
        # Agregação conforme solicitado
        if agregacao == 'trimestral':
            df['periodo'] = df['data'].dt.to_period('Q')
        elif agregacao == 'anual':
            df['periodo'] = df['data'].dt.to_period('Y')
        else:  # mensal
            df['periodo'] = df['data'].dt.to_period('M')
        
        # Série temporal total
        total_series = df.groupby('periodo').agg({
            'valor_fob': 'sum',
            'peso_kg': 'sum'
        }).reset_index()
        total_series['periodo_str'] = total_series['periodo'].astype(str)
        
        # Top 5 países ao longo do tempo
        top_paises = df.groupby('pais')['valor_fob'].sum().nlargest(5).index.tolist()
        paises_series = df[df['pais'].isin(top_paises)].groupby(['periodo', 'pais']).agg({
            'valor_fob': 'sum'
        }).reset_index()
        paises_series['periodo_str'] = paises_series['periodo'].astype(str)
        
        # Top 5 produtos ao longo do tempo
        top_produtos_ncm = df.groupby('ncm')['valor_fob'].sum().nlargest(5).index.tolist()
        produtos_df = df[df['ncm'].isin(top_produtos_ncm)].copy()
        
        # Adiciona descrição aos produtos
        if 'descricao_ncm' in produtos_df.columns:
            ncm_desc = produtos_df[['ncm', 'descricao_ncm']].drop_duplicates()
            produtos_series = produtos_df.groupby(['periodo', 'ncm']).agg({
                'valor_fob': 'sum'
            }).reset_index()
            produtos_series = produtos_series.merge(ncm_desc, on='ncm', how='left')
        else:
            produtos_series = produtos_df.groupby(['periodo', 'ncm']).agg({
                'valor_fob': 'sum'
            }).reset_index()
            produtos_series['descricao_ncm'] = 'NCM ' + produtos_series['ncm'].astype(str)
        
        produtos_series['periodo_str'] = produtos_series['periodo'].astype(str)
        
        return {
            'total': total_series,
            'volume': total_series[['periodo_str', 'peso_kg']].copy(),
            'top_paises': paises_series,
            'top_produtos': produtos_series
        }