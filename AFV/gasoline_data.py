"""Scrape eia.gov for annual average gas-prices.

Returns both a float and a tuple of floats. The current year's
gas prices are averaged from January to the present month.  Annual averages
starting from 2010 CY to last year are returned in the tuple.

    Typical usage example:

    >>> from gasoline_data import GasolineData
    >>> gas = GasolineData()
    >>> gas.current_avg()
    2.54
    >>> gas.historical_avg()
    [2.54, 2.99, 3.05, 3.13]

"""

import re
import pandas as pd
from urllib.request import urlopen
from pathlib import Path
from pyquery import PyQuery
from datetime import datetime
from typing import (
    Tuple,
    TypeVar,
    Dict,
    List,
)

# complex object types
webResponse = TypeVar('http.client.HTTPResponse')
pqObject = TypeVar('pyquery.pyquery.PyQuery')

ann_period = re.compile(r'\d\d\d\d')
mon_period = re.compile(r'\d\d\d\d\d\d')
general_val = re.compile(r'\d[.]\d+')
one_digit_val = re.compile(r'^\d$')

class _GasolineData2:

    def __init__(
            self,
            ann_url: str = (
            'https://www.eia.gov/opendata/qb.php?'
            'sdid=PET.EMM_EPMR_PTE_NUS_DPG.A'
            ),
            mon_url: str = (
                'https://www.eia.gov/opendata/qb.php?'
                'sdid=PET.EMM_EPMR_PTE_NUS_DPG.M'
            )
        ):
        self.ann_url = ann_url
        self.mon_url = mon_url

        self.ann_res = _get_response(ann_url)
        self.mon_res = _get_response(mon_url)

        for res in [self.ann_res, self.mon_res]:
            if res.status != 200:
                raise BadResponseError(res)

    @staticmethod
    def _get_response(eia_url: str) -> webResponse:
        return urlopen(eia_url)


class _GasolineData1(_GasolineData2):

    def __init__(self):

        ann: pqObject = PyQuery(self.ann_res.read())
        mon: pqObject = PyQuery(self.mon_res.read())

    

        self.ann_table = _column_parse(ann)
        self.mon_table = _column_parse(mon)

        for pq, table in {ann: self.ann_table, mon: self.mon_table}.items():
            rows = tuple(td.text for td in pq('td'))
            table['Series Name'] = _series_name_parse(rows)
            table['Period'] = _period_parse(rows)
            table['Frequency'] = _frequency_parse(rows)
            table['Value'] = _value_parse(rows)
            table['Unit'] = _unit_parse(rows)

            if len(set(len(v) for v in table.values())) != 1:
                raise FunkyTableDimensionsError(table)

    @staticmethod
    def _column_parse(eia_html: pqObject) -> Dict[str, None]:
        return dict.fromkeys(tuple(th.text for th in eia_html('th')))

    @staticmethod
    def _series_name_parse(eia_rows: Tuple[str]) -> Tuple[str]: 
        return tuple(
            i for i in eia_rows if 'U.S.' in i
            and 'Gasoline' in i and 'Prices,' in i
        )
    
    @staticmethod
    def _period_parse(eia_rows: Tuple[str]) -> Tuple[str]:
        return tuple(
            i for i in eia_rows
            if re.match(mon_period, i)
            or re.match(ann_period, i)
        )
    
    @staticmethod
    def _frequency_parse(eia_rows: Tuple[str]) -> Tuple[str]:
        return tuple(i for i in eia_rows if i == 'A' or i == 'M')
    
    @staticmethod
    def _value_parse(eia_rows: Tuple[str]) -> Tuple[str]:
        return tuple(
            i for i in eia_rows
            if re.match(general_val, i) or re.match(one_digit_val, i)
        )
    
    @staticmethod
    def _unit_parse(eia_rows: Tuple[str]) -> Tuple[str]:
        return tuple(i for i in eia_rows if i == 'Dollars per Gallon')

class GasolineData(_GasolineData1):

    def __init__(self):
        self.ann_data = pd.DataFrame(self.ann_table)
        self.mon_data = pd.DataFrame(self.mon_table)

        # cleaning up the date in the month-frame
        self.mon_data['Date'] = self.mon_data['Period'].apply(
            lambda x: datetime.strptime(x, '%Y%m')
        )

    def current_avg(self) -> float:
        return self.mon_data[
            self.mon_data['Date'].apply(lambda x: x.year == datetime.now().year)
        ]['Value'].apply(
            lambda x: float(x)
        ).mean()

    def historical_avg(self) -> List[float]:
        self.ann_data[
            (self.ann_data['Period'].apply(lambda x: int(x) >= 2010))
        ]['Value'].apply(lambda x: float(x)).to_list()

class FunkyTableDimensionsError(Exception):

    def __init__(self, table: Dict[str, Tuple[str]]):
        self.name = table['Series Name'][0].split()[-1]
        self.dimensions = str(tuple(len(v) for v in table.values()))

    def __str__(self):
        return f'{self.name}-table dimensions are off: {self.dimensions}'

class BadResponseError(Exception):

    def __init__(self, response: webResponse):
        self.response = response
    
    def __str__(self):
        return f'{self.response.status} response code: {self.response.reason}'