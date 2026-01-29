"""
Descompacta arquivos CSV se necessário
"""
from pathlib import Path
import zipfile

def descomprimir_datasets():
    """Descompacta CSVs se ainda não existirem"""
    datasets_dir = Path(__file__).parent / 'datasets'
    
    zip_files = list(datasets_dir.glob('*.zip'))
    
    if not zip_files:
        print("Nenhum arquivo ZIP encontrado.")
        return
    
    print(f"Verificando {len(zip_files)} arquivos ZIP...")
    
    descomprimidos = 0
    for zip_file in zip_files:
        csv_file = datasets_dir / f"{zip_file.stem}.csv"
        
        if csv_file.exists():
            print(f"  ✓ {csv_file.name} já existe")
            continue
        
        print(f"  Descomprimindo {zip_file.name}...")
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(datasets_dir)
        descomprimidos += 1
        print(f"    ✓ {csv_file.name} criado")
    
    if descomprimidos > 0:
        print(f"\n✓ {descomprimidos} arquivo(s) descomprimido(s)")
    else:
        print("\n✓ Todos os CSVs já estavam descomprimidos")

if __name__ == "__main__":
    descomprimir_datasets()
