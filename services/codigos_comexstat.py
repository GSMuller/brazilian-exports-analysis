"""
Mapeamento dos códigos utilizados nos dados do ComexStat
Baseado nas tabelas auxiliares do MDIC
"""
import pandas as pd
from pathlib import Path

# Cache para tabela NCM
_NCM_TABLE = None

def _load_ncm_table():
    """Carrega tabela NCM do governo (se disponível)"""
    global _NCM_TABLE
    if _NCM_TABLE is not None:
        return _NCM_TABLE
    
    try:
        # Tenta baixar tabela NCM-SH do governo
        url = "https://balanca.economia.gov.br/balanca/bd/tabelas/NCM_SH.csv"
        _NCM_TABLE = pd.read_csv(url, sep=';', encoding='latin1')
        return _NCM_TABLE
    except:
        return None

# Códigos de países (principais destinos de exportação brasileira)
PAISES = {
    '249': 'Estados Unidos',
    '058': 'Argentina',
    '169': 'China',
    '589': 'Países Baixos',
    '275': 'Alemanha',
    '061': 'Chile',
    '160': 'Japão',
    '399': 'Índia',
    '185': 'Coreia do Sul',
    '190': 'México',
    '493': 'Espanha',
    '072': 'Colômbia',
    '498': 'Itália',
    '245': 'Reino Unido',
    '531': 'Bélgica',
    '158': 'França',
    '087': 'Peru',
    '586': 'Polônia',
    '090': 'Paraguai',
    '246': 'Uruguai',
    '097': 'Venezuela',
    '593': 'Portugal',
    '235': 'Canadá',
    '570': 'Turquia',
    '155': 'Egito',
    '175': 'Emirados Árabes Unidos',
    '639': 'Rússia',
    '200': 'Malásia',
    '711': 'África do Sul',
    '230': 'Singapura',
    '505': 'Suíça',
    '225': 'Tailândia',
    '527': 'Áustria',
    '741': 'Vietnã',
    '265': 'Austrália',
    '075': 'Equador',
    '782': 'Bangladesh',
    '545': 'Dinamarca',
    '165': 'Indonésia',
}

# Códigos de vias de transporte
VIAS_TRANSPORTE = {
    '01': 'Marítima',
    '02': 'Fluvial',
    '03': 'Lacustre',
    '04': 'Aérea',
    '05': 'Postal',
    '06': 'Ferroviária',
    '07': 'Rodoviária',
    '08': 'Conduto/Rede Transmissão',
    '09': 'Meios Próprios',
    '10': 'Entrada/Saída ficta',
}

# Principais NCMs e suas descrições (expandido)
NCM_DESCRICOES = {
    # Commodities agrícolas
    '12011000': 'Soja em grão',
    '12019000': 'Outras sementes oleaginosas',
    '12099900': 'Outras sementes, frutos oleaginosos',
    '17011100': 'Açúcar de cana em bruto',
    '17011400': 'Outros açúcares de cana',
    '17019900': 'Outros açúcares',
    '10059000': 'Milho',
    '09011100': 'Café não torrado, não descafeinado',
    '09011200': 'Café não torrado, descafeinado',
    '52010000': 'Algodão não cardado nem penteado',
    '24012000': 'Tabaco parcialmente destalado',
    '08030000': 'Bananas frescas ou secas',
    
    # Carnes
    '02013000': 'Carne bovina desossada, fresca/refrigerada',
    '02023000': 'Carne bovina desossada, congelada',
    '02071400': 'Carne de frango congelada',
    '02072700': 'Pedaços e miudezas de galos/galinhas',
    '02032900': 'Outras carnes de suínos, congeladas',
    '01051100': 'Galos/galinhas, vivos',
    '05040090': 'Tripas de animais',
    
    # Minérios
    '26011100': 'Minério de ferro não aglomerado',
    '26011200': 'Minério de ferro aglomerado',
    '71081300': 'Ouro para uso não monetário',
    '74031100': 'Cátodos de cobre',
    '26030000': 'Minérios de cobre',
    '68029390': 'Outras pedras calcárias trabalhadas',
    
    # Petróleo e derivados
    '27090000': 'Óleos brutos de petróleo',
    '27101900': 'Outros óleos combustíveis',
    '27112900': 'Outros gases de petróleo liquefeitos',
    
    # Produtos processados
    '23040000': 'Tortas de óleo de soja',
    '47032900': 'Celulose química',
    '15079010': 'Óleo de soja refinado',
    '20090900': 'Suco de laranja',
    '20098990': 'Outros sucos de frutas',
    '44071000': 'Madeira serrada de coníferas',
    '17023000': 'Xarope de glicose',
    
    # Manufaturados
    '88024000': 'Aviões e veículos aéreos',
    '87032300': 'Automóveis 1500-3000 cm³',
    '84099190': 'Partes de motores diesel',
    '85258090': 'Outras câmeras',
    '87089900': 'Partes de veículos',
    '40118090': 'Outros pneumáticos novos de borracha',
    
    # Produtos diversos
    '73269090': 'Outras obras de ferro/aço',
    '20089900': 'Outras frutas preparadas',
    '19053100': 'Biscoitos doces',
    '38089192': 'Herbicidas',
    '64029900': 'Outros calçados',
    '19053200': 'Waffles e wafers',
    '49019900': 'Outros livros, brochuras',
    '33072010': 'Desodorantes corporais líquidos',
    '39251000': 'Reservatórios de plástico',
    
    # Mais exportações comuns do Brasil
    '12019100': 'Soja para semeadura',
    '17011100': 'Açúcar de cana em bruto',
    '02013000': 'Carne bovina desossada',
    '02071400': 'Carne de frango',
    '26011100': 'Minério de ferro',
    '27090010': 'Petróleo bruto',
    '47032900': 'Pasta química de madeira',
    '15079010': 'Óleo de soja refinado',
    '09011190': 'Outros cafés não torrados',
    '24012030': 'Tabaco parcialmente destalado',
    '52010000': 'Algodão',
    '12019000': 'Sementes de soja',
    '23040010': 'Tortas de soja',
    '02072600': 'Pedaços de frango',
    '02013000': 'Carne bovina fresca',
}

def get_pais_nome(codigo: str) -> str:
    """Retorna o nome do país dado o código"""
    codigo_str = str(codigo).zfill(3)
    return PAISES.get(codigo_str, f'País {codigo_str}')

def get_via_transporte(codigo: str) -> str:
    """Retorna o nome da via de transporte dado o código"""
    codigo_str = str(codigo).zfill(2)
    return VIAS_TRANSPORTE.get(codigo_str, f'Via {codigo_str}')

def get_ncm_descricao(codigo: str) -> str:
    """Retorna a descrição do NCM dado o código"""
    codigo_str = str(codigo).zfill(8)
    
    # Primeiro tenta buscar no dicionário manual
    if codigo_str in NCM_DESCRICOES:
        return NCM_DESCRICOES[codigo_str]
    
    # Busca no dicionário completo gerado automaticamente
    try:
        from .ncm_completo import NCM_COMPLETO
        if codigo_str in NCM_COMPLETO:
            return NCM_COMPLETO[codigo_str]
    except ImportError:
        pass
    
    # Tenta buscar na tabela do governo
    ncm_table = _load_ncm_table()
    if ncm_table is not None:
        try:
            match = ncm_table[ncm_table['CO_NCM'] == int(codigo)]
            if not match.empty:
                return match.iloc[0]['NO_NCM_POR']
        except:
            pass
    
    # Se não encontrar, retorna código com formatação melhor
    # NCM tem 8 dígitos: XX.XX.XX.XX (capítulo.posição.subposição.item)
    formatted = f"{codigo_str[:2]}.{codigo_str[2:4]}.{codigo_str[4:6]}.{codigo_str[6:]}"
    return f"NCM {formatted}"
