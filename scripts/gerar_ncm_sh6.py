"""
Extrai NCMs e descrições direto dos CSVs do ComexStat
Os CSVs NÃO têm as descrições, apenas códigos
Vou usar a tabela SH6 do governo como base
"""
import pandas as pd
from pathlib import Path

def gerar_dicionario_sh6():
    """Gera dicionário usando tabela SH6"""
    print("Carregando tabela SH6...")
    
    df = pd.read_csv('NCM_SH.csv')
    print(f"Registros SH6: {len(df)}")
    
    #Cria dicionário SH6 (6 primeiros dígitos do NCM)
    sh6_dict = {}
    for _, row in df.iterrows():
        sh6 = str(row['CO_SH6']).zfill(6)
        desc = str(row['NO_SH6_POR']).strip()
        sh6_dict[sh6] = desc
    
    # Lê NCMs usados
    with open('ncms_unicos.txt', 'r') as f:
        ncms = [line.strip() for line in f]
    
    print(f"NCMs únicos: {len(ncms)}")
    
    # Mapeia NCMs usando os 6 primeiros dígitos
    ncm_dict = {}
    for ncm in ncms:
        sh6 = ncm[:6]
        if sh6 in sh6_dict:
            ncm_dict[ncm] = sh6_dict[sh6]
        else:
            # Tenta com 4 dígitos (SH4)
            sh4 = ncm[:4]
            ncm_dict[ncm] = f"Produto NCM {ncm[:2]}.{ncm[2:4]}.{ncm[4:6]}.{ncm[6:]}"
    
    print(f"NCMs mapeados: {len(ncm_dict)}")
    
    # Gera arquivo Python
    output = Path('services') / 'ncm_completo.py'
    with open(output, 'w', encoding='utf-8') as f:
        f.write('"""\nDicionário de NCMs - Gerado automaticamente\n"""\n\n')
        f.write('NCM_COMPLETO = {\n')
        for ncm in sorted(ncm_dict.keys()):
            desc = ncm_dict[ncm].replace("'", "\\'").replace('"', '\\"').replace('\n', ' ').replace('\\', ' ')
            # Remove qualquer caracter de controle
            desc = ''.join(char for char in desc if ord(char) >= 32 or char == ' ')
            f.write(f"    '{ncm}': '{desc}',\n")
        f.write('}\n')
    
    print(f"✓ Salvo em: {output}")
    
    # Exemplos
    print("\\nExemplos:")
    for ncm in sorted(ncm_dict.keys())[:20]:
        print(f"  {ncm}: {ncm_dict[ncm]}")

if __name__ == "__main__":
    gerar_dicionario_sh6()
