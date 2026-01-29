"""
Script para extrair todos os NCMs únicos dos CSVs e gerar dicionário completo
"""
import pandas as pd
from pathlib import Path
import json

def extrair_ncms():
    datasets_dir = Path(__file__).parent / 'datasets'
    
    # Dicionário para armazenar NCM -> descrição
    ncm_dict = {}
    
    # Processa cada arquivo CSV
    csv_files = list(datasets_dir.glob('EXP_*.csv'))
    
    print(f"Encontrados {len(csv_files)} arquivos CSV")
    
    for csv_file in csv_files:
        print(f"\nProcessando {csv_file.name}...")
        
        try:
            # Lê apenas as colunas necessárias
            df = pd.read_csv(csv_file, sep=';', encoding='latin1', 
                           usecols=['CO_NCM'], 
                           dtype={'CO_NCM': str})
            
            # Remove aspas se existirem
            df['CO_NCM'] = df['CO_NCM'].str.replace('"', '')
            
            # Pega NCMs únicos
            ncms_unicos = df['CO_NCM'].unique()
            
            print(f"  Encontrados {len(ncms_unicos)} NCMs únicos neste arquivo")
            
            for ncm in ncms_unicos:
                ncm_clean = str(ncm).zfill(8)
                if ncm_clean not in ncm_dict:
                    ncm_dict[ncm_clean] = None
                    
        except Exception as e:
            print(f"  Erro ao processar {csv_file.name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"TOTAL DE NCMs ÚNICOS: {len(ncm_dict)}")
    print(f"{'='*60}")
    
    # Salva lista de NCMs
    output_file = Path(__file__).parent / 'ncms_unicos.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        for ncm in sorted(ncm_dict.keys()):
            f.write(f"{ncm}\n")
    
    print(f"\nLista salva em: {output_file}")
    
    # Mostra alguns exemplos
    print("\nPrimeiros 20 NCMs:")
    for ncm in sorted(ncm_dict.keys())[:20]:
        print(f"  {ncm}")

if __name__ == "__main__":
    extrair_ncms()
