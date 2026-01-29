# Scripts Utilitários

Scripts de manutenção e setup do projeto.

## Scripts Disponíveis

### download_data.py
Baixa dados anuais de exportação do ComexStat (Ministério da Economia).

```bash
python scripts/download_data.py
```

Baixa arquivos EXP_2020.csv até EXP_2024.csv (475 MB total).

### descomprimir_datasets.py
Extrai arquivos CSV dos arquivos ZIP comprimidos.

```bash
python scripts/descomprimir_datasets.py
```

Executado automaticamente durante o build do Docker.

### extrair_ncms.py
Extrai lista de NCMs únicos dos datasets para mapeamento.

```bash
python scripts/extrair_ncms.py
```

Gera arquivo `scripts/data/ncms_unicos.txt` com todos os códigos NCM encontrados.

### gerar_ncm_sh6.py
Gera dicionário completo de NCMs usando tabela SH6 do governo.

```bash
python scripts/gerar_ncm_sh6.py
```

Baixa NCM_SH.csv do site oficial e gera `services/ncm_completo.py` com 9.301 mapeamentos.

### gerar_dicionario_ncm.py
Versão anterior do gerador de dicionário NCM (deprecated).

### test_server.py
Script de teste do servidor Flask.

```bash
python scripts/test_server.py
```

## Ordem de Execução

Para setup completo do zero:

```bash
# 1. Baixar dados
python scripts/download_data.py

# 2. Comprimir para Git (manual, usar 7zip/WinRAR)
# zip -9 datasets/EXP_2024.zip datasets/EXP_2024.csv

# 3. Extrair NCMs
python scripts/extrair_ncms.py

# 4. Gerar dicionário
python scripts/gerar_ncm_sh6.py

# 5. Descomprimir para uso
python scripts/descomprimir_datasets.py
```

## Arquivos Temporários

Os scripts utilizam a pasta `scripts/data/` para armazenar arquivos temporários:

- `ncms_unicos.txt`: Lista de NCMs únicos extraídos
- `NCM_SH.csv`: Tabela de classificação SH6 do governo

Estes arquivos são ignorados pelo Git (.gitignore).
