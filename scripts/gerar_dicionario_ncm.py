"""
Baixa tabela NCM oficial e gera dicionário Python completo
"""
import pandas as pd
import requests
from pathlib import Path

def baixar_tabela_ncm():
    """Baixa tabela NCM-SH do governo"""
    print("Baixando tabela NCM oficial do governo...")
    
    url = "https://balanca.economia.gov.br/balanca/bd/tabelas/NCM_SH.csv"
    
    try:
        df = pd.read_csv(url, sep=';', encoding='latin1')
        print(f"✓ Tabela baixada: {len(df)} registros")
        
        # Salva localmente
        output = Path(__file__).parent / 'NCM_SH.csv'
        df.to_csv(output, index=False, encoding='utf-8')
        print(f"✓ Salvo em: {output}")
        
        return df
    except Exception as e:
        print(f"✗ Erro ao baixar: {e}")
        return None

def gerar_dicionario_ncm(df_ncm):
    """Gera arquivo Python com dicionário de NCMs"""
    print("\nGerando dicionário Python...")
    
    # Lê NCMs únicos do nosso export
    ncms_file = Path(__file__).parent / 'ncms_unicos.txt'
    with open(ncms_file, 'r') as f:
        ncms_usados = set(line.strip() for line in f)
    
    print(f"NCMs nos nossos dados: {len(ncms_usados)}")
    print(f"NCMs na tabela oficial: {len(df_ncm)}")
    
    # Cria dicionário
    ncm_dict = {}
    
    # Remove aspas da coluna NCM se existir
    df_ncm['CO_NCM'] = df_ncm['CO_NCM'].astype(str).str.replace('"', '').str.zfill(8)
    df_ncm['NO_NCM_POR'] = df_ncm['NO_NCM_POR'].astype(str).str.replace('"', '')
    
    for _, row in df_ncm.iterrows():
        ncm = str(row['CO_NCM']).zfill(8)
        descricao = row['NO_NCM_POR']
        
        # Só adiciona se estiver nos nossos dados
        if ncm in ncms_usados:
            # Limpa descrição
            descricao = descricao.strip()
            descricao = descricao.replace("'", "\\'")  # Escapa aspas simples
            ncm_dict[ncm] = descricao
    
    print(f"NCMs mapeados: {len(ncm_dict)}")
    
    # Gera arquivo Python
    output_file = Path(__file__).parent / 'services' / 'ncm_completo.py'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('"""\n')
        f.write('Dicionário completo de NCMs gerado automaticamente\n')
        f.write('Fonte: Tabela NCM-SH do Ministério da Economia\n')
        f.write(f'Total de {len(ncm_dict)} NCMs\n')
        f.write('"""\n\n')
        f.write('NCM_COMPLETO = {\n')
        
        for ncm in sorted(ncm_dict.keys()):
            desc = ncm_dict[ncm]
            f.write(f"    '{ncm}': '{desc}',\n")
        
        f.write('}\n')
    
    print(f"\n✓ Dicionário salvo em: {output_file}")
    print(f"✓ Total de {len(ncm_dict)} NCMs mapeados")
    
    return ncm_dict

if __name__ == "__main__":
    # Baixa tabela
    df = baixar_tabela_ncm()
    
    if df is not None:
        # Gera dicionário
        ncm_dict = gerar_dicionario_ncm(df)
        
        # Mostra alguns exemplos
        print("\nExemplos de mapeamentos:")
        for i, (ncm, desc) in enumerate(sorted(ncm_dict.items())[:10]):
            print(f"  {ncm}: {desc}")
        
        print("\n✓ Concluído!")
    else:
        print("\n✗ Falha ao gerar dicionário")
