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
from unidecode import unidecode

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

def url_builder(state: str, site: str = 'caixa') -> str:
    """
    Function to build the URL to download the data.

    Parameters
    ----------
    state : str
        Desired state to download the data
    site : str, optional
        Desired site to download the data, by default 'caixa'

    Returns
    -------
    str
        URL to download the data

    Raises
    ------
    NotImplementedError
        If the builder for desired site doesn't exists throws an error.
    """
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
    """
    Function to download the data from the desired URL.

    Parameters
    ----------
    data_url : str
        URL to download the data
    sep : str
        Columns separators
    decimal : str
        Character to recognize as decimal point
    thousand_separator : str
        Thousands separator
    skiprows : int
        Number of lines to skip at the start of the file
    encoding : str
        Encoding to use for UTF when reading. [List of Python standard encodings](https://docs.python.org/3/library/codecs.html#standard-encodings)
    bad_lines_fixing : Callable[[list[str]], list[str]], optional
        Specifies what to do upon encountering a bad line (a line with too many fields), by default None

    Returns
    -------
    pd.DataFrame
        Data frame containing the downloaded data.
    """

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
    """
    Function to adjust the auctions data.

    Parameters
    ----------
    data_df : pd.DataFrame
        Data to be adjusted
    columns_names : dict[str]
        Mapping of the columns names to be renamed. Like: {'Old_name':'New_name'}.

    Returns
    -------
    pd.DataFrame
        Adjusted data.
    """

    # Copy data to avoid problems with Python pointer's.
    data = data_df.copy()

    # Renaming columns.
    data.rename(columns=columns_names, inplace=True)

    # Removing white spaces at the end of each string.
    data['City'] = data['City'].str.replace('(\s?)$','',regex=True)
    data['State'] = data['State'].str.replace('(\s?)$','',regex=True)

    # Checkin if discount values is greater than 100% and than adjusting it. 
    ## This can occur because the use of dot as decimal and thousand separator.
    data['Discount'] = data['Discount'].apply(lambda xrow: xrow/100 if xrow>100 else xrow)

    # Creating the categories based on description.
    data['Category'] = data['Description'].apply(lambda s: unidecode(s.split(',')[0]).upper())

    # Adjusting column Modality:
    data['Modality'] = data['Modality'].apply(lambda s: unidecode(s).upper())
    data['Modality'] = data['Modality'].str.replace('1O','1').str.replace('2O','2')

    return data

def bad_lines_fixing(bad_line: list[str]) -> list[str]:
    """
    Function to adjust 'bad lines' in reading data usind pandas.

    Parameters
    ----------
    bad_line : list[str]
        List containing the row of the bad line, containing wrong number of elements (columns)

    Returns
    -------
    list[str]
        List with the correct number of elements (columns)
    """
    # The bad lines are because the use of ';' in 'Adress' column. After comes columns 'Prince' and 'Appraisal'.
    fixed_line = bad_line[:4]+[' '.join(bad_line[4:-6])] + bad_line[-6:] 
    return fixed_line

def get_auctions_data(state :str, site: str = 'caixa') -> pd.DataFrame:
    """
    Function to get the final data (download and adjust) from specific site and state.

    Parameters
    ----------
    state : str
        Desired state
    site : str, optional
        Desired site to download, by default 'caixa'

    Returns
    -------
    pd.DataFrame
        Final data from the site and state

    Raises
    ------
    NotImplementedError
        If there is no implementation for desired site, throws an error.
    """
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
    """
    Function to filter the data based on conditions.

    Parameters
    ----------
    data_df : pd.DataFrame
        Data to be filterd
    city : str, optional
        Desired city, by default None
    category : str, optional
        Desired auction category, by default None
    lower_price : float, optional
        Desired minimum price, by default None
    upper_price : float, optional
        Desired maximum price, by default None
    modality : str, optional
        Desired auction modality, by default None

    Returns
    -------
    pd.DataFrame
        Data filtered
    """

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

    # Resetting the index to easy the comparison between dataframes.
    df.reset_index(drop=True, inplace=True)

    return df