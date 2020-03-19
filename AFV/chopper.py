import pandas as pd
from dataclasses import dataclass

from AFV.flipper import (
    _FlippedClean,  # to subclass
    pdDataFrame,  # typevar
)

@dataclass
class _Chopped(_FlippedClean):

    def __post_init__(self):
        self.fcev = self._fcev_chop()
        self.hev = self._hev_chop()
        self.phev = self._phev_chop()
        self.bev = self._bev_chop()
        self.sales = self._sales_chop()
    
    def _sales_chop(self) -> pdDataFrame:
        sales = self.shinychrome[
            (~self.shinychrome['CLEAN_3'].str.contains('cumulative'))
            & (self.shinychrome['CLEAN_3'].str.contains('sales'))
            & (self.shinychrome['CLEAN_3'].str.contains('share'))
            & (
                (~self.shinychrome['LEVEL_1'].isna())
                | (self.shinychrome['CLEAN_2'] == '(blank)')
            )
        ].copy()
        sales.drop(
            ['LEVEL_0',
             'LEVEL_1',
             'LEVEL_2',
             'LEVEL_3',
             'CLEAN_0',
             'CLEAN_1',
             'CLEAN_2'],
            axis=1,
            inplace=True,
        )
        sales.rename(columns={'CLEAN_3': 'SALES'}, inplace=True)
        sales.set_index(
            sales['SALES'].apply(lambda x: x.replace('_', ' ').upper()),
            inplace=True,
        )
        sales.drop('SALES', axis=1, inplace=True)
        sales.drop('ALT-FUEL VEHICLE SALES', axis='index', inplace=True,)
        sales.fillna(0, inplace=True)
        return sales

    def _fcev_chop(self) -> pdDataFrame:
        fcev = self.shinychrome[
            (self.shinychrome['CLEAN_0'] == 'fcev')
            & (
                # filtering out models
                (self.shinychrome['CLEAN_1'] == 'toyota')
                | (self.shinychrome['CLEAN_1'] == 'competitor')
            )
            & (
                (self.shinychrome['CLEAN_3'] == 'total_us')
                | (self.shinychrome['CLEAN_2'] != 'mirai')
            )
        ].copy()
        return _ptdf_chop(fcev)

    def _hev_chop(self) -> pdDataFrame:
        hev = self.shinychrome[
            (self.shinychrome['CLEAN_0'] == 'hev')
            & (
                (self.shinychrome['CLEAN_1'] == 'toyota')
                | (self.shinychrome['CLEAN_1'] == 'competitor')
            )
            & (
                (self.shinychrome['CLEAN_3'].str.contains('total_us'))
                & (~self.shinychrome['CLEAN_3'].str.contains('hawaii'))
                & (self.shinychrome['CLEAN_3'] != 'total_us_prius_family')
                | (self.shinychrome['CLEAN_1'] != 'toyota')
            )
        ].copy()
        return _ptdf_chop(hev)


    def _phev_chop(self) -> pdDataFrame:
        phev = self.shinychrome[
            (self.shinychrome['CLEAN_0'] == 'phev')
            & (
                (self.shinychrome['CLEAN_1'] == 'toyota')
                | (self.shinychrome['CLEAN_1'] == 'competitor')
            )
        ].copy()
        return _ptdf_chop(phev)

    def _bev_chop(self) -> pdDataFrame:
        bev = self.shinychrome[
            (self.shinychrome['CLEAN_0'] == 'bev')
            & (
                (self.shinychrome['CLEAN_1'] == 'toyota')
                | (self.shinychrome['CLEAN_1'] == 'competitor')
            )
        ].copy()
        return _ptdf_chop(bev)

    @staticmethod
    def _ptdf_chop(ptdf: pdDataFrame) -> pdDataFrame:
        ptdf = ptdf.copy()
        ptdf.drop(
            ['LEVEL_0', 'LEVEL_1', 'LEVEL_2', 'LEVEL_3'], axis=1, inplace=True,
        )
        ptdf.rename(
            columns={
                'CLEAN_0': 'PT_TYPE',
                'CLEAN_1': 'TOYO/COMP',
                'CLEAN_2': 'BRAND',
                'CLEAN_3': 'NAMEPLATE',
            },
            inplace=True,
        )
        return ptdf