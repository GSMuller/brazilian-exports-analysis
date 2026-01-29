import pandas as pd
from pathlib import Path

# Lê CSV de dezembro 2024
datasets_dir = Path(__file__).parent.parent / 'datasets'
csv_file = datasets_dir / 'EXP_2024.csv'

if csv_file.exists():
    print(f"Lendo {csv_file.name}...")
    df = pd.read_csv(csv_file, sep=';', encoding='latin1', nrows=100000)
    
    # Remove aspas
    df.columns = df.columns.str.replace('"', '')
    
    # Filtra dezembro
    if 'CO_MES' in df.columns:
        df = df[df['CO_MES'].astype(int) == 12]
        print(f"Registros de dezembro: {len(df)}")
    
    # Agrupa por país e soma valores
    if 'CO_PAIS' in df.columns and 'VL_FOB' in df.columns:
        # Converte VL_FOB para numérico
        df['VL_FOB'] = pd.to_numeric(df['VL_FOB'].astype(str).str.replace('"', ''), errors='coerce')
        
        # Agrupa e ordena
        top_paises = df.groupby('CO_PAIS')['VL_FOB'].sum().sort_values(ascending=False).head(15)
        
        print("\nTop 15 países por valor FOB:")
        print("Código | Valor FOB")
        print("-" * 40)
        for cod, valor in top_paises.items():
            print(f"{str(cod).zfill(3)} | ${valor:,.2f}")
else:
    print("Arquivo não encontrado!")
