import pandas as pd
import numpy as np

# Simula dados reais
data = {
    'produto': ['Soja', 'Minério Fe', 'Petróleo', 'Café', 'Carne'],
    'valor_fob': [1000000000, 500000000, 300000000, 50000000, 20000000],  # valores muito diferentes
    'peso_kg': [10000000, 5000000, 3000000, 1000000, 500000],
    'preco_medio_kg': [100, 100, 100, 50, 40]
}

df = pd.DataFrame(data)

print("=== DADOS ORIGINAIS ===")
print(df[['produto', 'valor_fob']])
print(f"\nValor mínimo: ${df['valor_fob'].min():,.0f}")
print(f"Valor máximo: ${df['valor_fob'].max():,.0f}")
print(f"Razão max/min: {df['valor_fob'].max() / df['valor_fob'].min():.1f}x")

# Teste 1: Abordagem atual (sizeref)
print("\n=== TESTE 1: Com sizeref (abordagem atual) ===")
sizeref = 2. * df['valor_fob'].max() / (60.**2)
print(f"sizeref = {sizeref:,.0f}")
df['size_plotly'] = df['valor_fob'] / sizeref
print(df[['produto', 'size_plotly']])

# Teste 2: Normalização linear
print("\n=== TESTE 2: Normalização Linear ===")
min_size = 10
max_size = 80
values = df['valor_fob'].values
normalized = (values - values.min()) / (values.max() - values.min())
df['size_linear'] = normalized * (max_size - min_size) + min_size
print(df[['produto', 'size_linear']])

# Teste 3: Raiz quadrada (mais suave)
print("\n=== TESTE 3: Com Raiz Quadrada ===")
sqrt_values = np.sqrt(values)
normalized_sqrt = (sqrt_values - sqrt_values.min()) / (sqrt_values.max() - sqrt_values.min())
df['size_sqrt'] = normalized_sqrt * (max_size - min_size) + min_size
print(df[['produto', 'size_sqrt']])

# Teste 4: Log10 (mais suave ainda)
print("\n=== TESTE 4: Com Log10 ===")
log_values = np.log10(values + 1)
normalized_log = (log_values - log_values.min()) / (log_values.max() - log_values.min())
df['size_log'] = normalized_log * (max_size - min_size) + min_size
print(df[['produto', 'size_log']])

print("\n=== RECOMENDAÇÃO ===")
print("Para visualizar diferenças: use Normalização Linear ou Raiz Quadrada")
print("sizeref do Plotly pode não funcionar bem com valores muito grandes")
