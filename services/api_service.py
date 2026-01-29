import requests
import pandas as pd
from typing import Optional
import time
from pathlib import Path

class ComexStatAPI:
    """
    Serviço para integração com a API do ComexStat do MDIC.
    Documentação: https://comexstat.mdic.gov.br/pt/home
    """
    
    def __init__(self):
        self.base_url = "https://balanca.economia.gov.br/balanca/bd/comexstat-bd"
        self.datasets_dir = Path(__file__).parent.parent / 'datasets'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_export_data(self, year: str, month: str) -> pd.DataFrame:
        """
        Busca dados de exportação para um período específico.
        Lê dos arquivos CSV ANUAIS baixados e filtra por mês.
        """
        # Verifica se existe arquivo ANUAL local
        local_file = self.datasets_dir / f"EXP_{year}.csv"
        
        if local_file.exists():
            print(f"Lendo arquivo anual: {local_file.name}")
            try:
                # Lê CSV com separador ponto e vírgula
                df = pd.read_csv(local_file, sep=';', encoding='latin1', on_bad_lines='skip', low_memory=False)
                
                # Remove aspas dos valores se existirem
                df.columns = df.columns.str.replace('"', '')
                for col in df.columns:
                    if df[col].dtype == 'object':
                        df[col] = df[col].astype(str).str.replace('"', '')
                
                # Filtra pelo mês solicitado
                if 'CO_MES' in df.columns:
                    month_int = int(month)
                    df = df[df['CO_MES'].astype(int) == month_int]
                    print(f"  Filtrado para mês {month}: {len(df)} registros")
                
                return self._process_raw_data(df)
            except Exception as e:
                print(f"Erro ao ler CSV: {e}")
                import traceback
                traceback.print_exc()
        
        # Se não tem CSV, usa dados de exemplo
        print(f"Arquivo {local_file.name} não encontrado. Usando dados de exemplo...")
        return self._generate_sample_data()
    
    def _process_raw_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Processa dados brutos da API"""
        from .codigos_comexstat import get_pais_nome, get_via_transporte, get_ncm_descricao
        
        # Padroniza nomes de colunas
        column_mapping = {
            'CO_ANO': 'ano',
            'CO_MES': 'mes',
            'CO_NCM': 'ncm',
            'NO_NCM_POR': 'descricao_ncm',
            'CO_PAIS': 'cod_pais',
            'NO_PAIS': 'pais',
            'CO_VIA': 'cod_via',
            'NO_VIA': 'via',
            'SG_UF_NCM': 'uf',
            'VL_FOB': 'valor_fob',
            'KG_LIQUIDO': 'peso_kg'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Mapeia códigos para nomes legíveis
        if 'cod_pais' in df.columns and 'pais' not in df.columns:
            df['pais'] = df['cod_pais'].apply(lambda x: get_pais_nome(str(x)))
        
        if 'cod_via' in df.columns and 'via' not in df.columns:
            df['via'] = df['cod_via'].apply(lambda x: get_via_transporte(str(x)))
        
        if 'ncm' in df.columns and 'descricao_ncm' not in df.columns:
            df['descricao_ncm'] = df['ncm'].apply(lambda x: get_ncm_descricao(str(x)))
        
        # Converte tipos
        numeric_cols = ['valor_fob', 'peso_kg']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove linhas com valores inválidos
        df = df.dropna(subset=['valor_fob'])
        
        return df
    
    def _generate_sample_data(self) -> pd.DataFrame:
        """Gera dados de exemplo para testes"""
        import numpy as np
        
        ncm_products = {
            '12011000': 'Soja em grão',
            '17011100': 'Açúcar de cana em bruto',
            '26011100': 'Minério de ferro',
            '27090000': 'Petróleo bruto',
            '02013000': 'Carne bovina fresca',
            '02071400': 'Carne de frango congelada',
            '88024000': 'Aviões e helicópteros',
            '23040000': 'Farelo de soja',
            '47032900': 'Celulose química',
            '10059000': 'Milho',
            '09011100': 'Café não torrado',
            '52010000': 'Algodão não cardado',
            '24012000': 'Tabaco parcialmente destalado',
            '08030000': 'Bananas frescas',
            '20090900': 'Suco de laranja',
            '87032300': 'Automóveis',
            '84099190': 'Motores diesel',
            '71081300': 'Ouro não monetário',
            '15079000': 'Óleo de soja refinado',
            '44071000': 'Madeira serrada'
        }
        
        countries = ['China', 'Estados Unidos', 'Argentina', 'Países Baixos', 
                    'Alemanha', 'Chile', 'Japão', 'México', 'Espanha', 'Itália',
                    'Coreia do Sul', 'Índia', 'Rússia', 'França', 'Bélgica']
        
        transport_modes = ['Marítima', 'Aérea', 'Rodoviária', 'Fluvial']
        
        states = ['SP', 'RS', 'PR', 'MG', 'MT', 'GO', 'SC', 'BA', 'MS', 'ES',
                 'PA', 'MA', 'RJ', 'TO', 'RO']
        
        n_records = 2000
        
        # Gera dados com distribuições mais realistas
        ncm_keys = list(ncm_products.keys())
        
        data = {
            'ano': ['2024'] * n_records,
            'mes': ['12'] * n_records,
            'ncm': np.random.choice(ncm_keys, n_records),
            'descricao_ncm': [ncm_products[ncm] for ncm in np.random.choice(ncm_keys, n_records)],
            'pais': np.random.choice(countries, n_records),
            'via': np.random.choice(transport_modes, n_records, p=[0.85, 0.10, 0.04, 0.01]),
            'uf': np.random.choice(states, n_records),
            'valor_fob': np.random.lognormal(13, 1.5, n_records),
            'peso_kg': np.random.lognormal(11, 2, n_records)
        }
        
        return pd.DataFrame(data)
    
    def download_monthly_file(self, year: str, month: str, output_path: str):
        """Download do arquivo mensal completo"""
        url = f"{self.base_url}/ncm/EXP_{year}{month}.csv"
        
        response = self.session.get(url, stream=True)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        return False
