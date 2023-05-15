# -*- coding: utf-8 -*-
"""
Data acquisiton of auctions

"""

# Preventing __pycache__
import sys
sys.dont_write_bytecode = True

# Common imports
import pandas as pd
from typing import Callable

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

FILTER_TYPES = {
    0:'State',
    1:'City',
    2:'Category',
    3:'Modality',
    4:'LowerPrice',
    5:'UpperPrice'
}

# data = pd.read_csv('https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_SC.csv', sep=';', encoding='ISO-8859-1', skiprows=2)

def url_builder(state: str, site: str = 'caixa') -> str:
    if site=='caixa':
        url_data = 'https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_{}.csv'.format(state)
    else:
        raise NotImplementedError('Invalid Site!')
    
    return url_data

def download_data(
        data_url: str, 
        sep: str, 
        decimal: str, 
        thousand_separator: str, 
        skiprows: int,
        encoding: str,
        bad_lines_fixing: Callable[[list[str]], list[str]] = None
        ) -> pd.DataFrame:

    # If there is no way to fix bad lines(or they did not exists), sets the default value for pandas method.
    if bad_lines_fixing is None:
        bad_lines_fixing = 'error'
        engine = 'c'
    else:
        engine = 'python'

    # Reading the csv.
    data = pd.read_csv(
        data_url, sep=sep, decimal=decimal, thousands=thousand_separator, 
        encoding=encoding, skiprows=skiprows, on_bad_lines=bad_lines_fixing, engine=engine)

    return data

def adjust_data(data_df: pd.DataFrame, columns_names: dict[str]) -> pd.DataFrame:

    # Copy data to avoid problems with Python pointer's.
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

def bad_lines_fixing(bad_line: list[str]) -> list[str]:
    # The bad lines are because the use of ';' in 'Adress' column.
    fixed_line = bad_line[:4]+[bad_line[4] + bad_line[5]] + bad_line[6:] 
    return fixed_line

def get_auctions_data(state :str, site: str = 'caixa') -> pd.DataFrame:
    if site != 'caixa':
        raise NotImplementedError('Invalid Site!')
    
    # Dowloading the data.
    data = download_data(
        data_url=url_builder(state=state),
        sep=';',
        decimal=',',
        thousand_separator='.',
        encoding='ISO-8859-1',
        skiprows=2,
        bad_lines_fixing=bad_lines_fixing
        )

    # Adjusting data columns and values.
    data = adjust_data(data, columns_names=COLUMNS_NAMES_MAP)

    return data


def filter_data(
        data_df: pd.DataFrame, 
        city: str = None, 
        category: str = None, 
        lower_price: float = None, 
        upper_price: float = None,
        modality: str = None) -> pd.DataFrame:

    # Copy data to avoid problems with Python pointer's.
    df = data_df.copy()

    # Checking filters conditions.
    if not pd.isnull(city):
        df = df.loc[df['City']==city]

    if not pd.isnull(category):
        df = df.loc[df['Category']==category]

    if not pd.isnull(modality):
        df = df.loc[df['Modality']==modality]

    if (not pd.isnull(lower_price)) & (not pd.isnull(upper_price)):
        df = df.loc[ (df['Price'] >= lower_price ) & (df['Price'] <= upper_price)]

    elif not pd.isnull(lower_price):
        df = df.loc[df['Price'] >= lower_price ]

    elif not pd.isnull(upper_price):
        df = df.loc[df['Price'] <= upper_price ]

    return df