# -*- coding: utf-8 -*-
"""
Data acquisiton of auctions

"""

# Preventing __pycache__
import sys
sys.dont_write_bytecode = True

# Common imports
import pandas as pd

data = pd.read_csv('https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_SC.csv', sep=';', encoding='ISO-8859-1', skiprows=2)

print(data)


