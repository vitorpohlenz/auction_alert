# -*- coding: utf-8 -*-
"""
Data acquisiton of auctions

"""

# Preventing __pycache__
import sys
sys.dont_write_bytecode = True

# Common imports
import pandas as pd

# Constants
COLUMNS_NAMES_MAP = {
    ' N° do imóvel':'Id',
    'UF':'State', 
    'Cidade':'City', 
    'Bairro':'District', 
    'Endereço':'Adress', 
    'Preço':'Price',
    'Valor de avaliação':'Appraisal',
    'Desconto':'Discount',
    'Descrição':'Description',
    'Modalidade de venda':'Modality',
    'Link de acesso':'Link'
}

# data = pd.read_csv('https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_SC.csv', sep=';', encoding='ISO-8859-1', skiprows=2)

def download_data(data_url: str, sep: str, decimal: str, thousand_separator: str, encoding: str, skiprows: int) -> pd.DataFrame:
    
    data = pd.read_csv(data_url, sep=sep, decimal=decimal, thousands=thousand_separator, encoding=encoding, skiprows=skiprows)

    return data

def adjust_data(data_df: pd.DataFrame, columns_names: dict[str]) -> pd.DataFrame:

    data = data_df.copy()

    # Renaming columns.
    data.rename(columns=columns_names, inplace=True)

    # Removing white spaces at the end of each string.
    data['City'] = data['City'].str.replace('(\s?)$','',regex=True)

    # Checkin if discount values is greater than 100% and than adjusting it. 
    ## This can occur because the use of dot as decimal and thousand separator.
    data['Discount'] = data['Discount'].apply(lambda xrow: xrow/100 if xrow>100 else xrow)

    # Creating the categories based on description.
    data['Category'] = data['Description'].apply(lambda s: s.split(',')[0])
    
    return data

data = download_data(
    data_url='https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_SC.csv',
    sep=';',
    decimal=',',
    thousand_separator='.',
    encoding='ISO-8859-1',
    skiprows=2
    )

data = adjust_data(data, columns_names=COLUMNS_NAMES_MAP)

print(data)


