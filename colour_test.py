# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 17:41:21 2021

@author: amlut
"""

# colour_test

from Dice import Dice

from bokeh.io import show
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, TableColumn, HTMLTemplateFormatter

from bokeh.sampledata.periodic_table import elements

elements['name_lower'] = elements['name'].str.lower()
source = ColumnDataSource(elements)
print(source.data)

columns = [
    TableColumn(field='atomic number', title='Atomic Number'),
    TableColumn(field='symbol', title='Symbol'),
    TableColumn(field='name', title='Name', 
                formatter=HTMLTemplateFormatter(template='<font color="<%= Dice.hex_colour[1] %>"><%= value %></font>'))
]
data_table = DataTable(source=source, columns=columns, editable=False)

show(data_table)