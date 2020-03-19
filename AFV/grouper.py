import pandas as pd
from dataclasses import dataclass
from AFV.chopper import (
    Chopped,
    pdDataFrame,
)

@dataclass
class Grouper(_Chopped):

    def __post_init__(self):
        self.frames = {
            'orig': self.shinychrome,
            'fcev': self.fcev,
            'hev': self.hev,
            'phev': self.phev,
            'bev': self.bev,
            'sales': self.sales,
        }

    @staticmethod
    def _group_brands(ptdf: pdDataFrame) -> pdDataFrame:
        dummy = (
            ptdf
            .set_index(['TOYO/COMP', 'BRAND'])
            .loc[:, [c for c in ptdf.columns
                if 'CY ' in c and int(c[3:]) > 2009]
            ]
        ).copy().reset_index()
        dummy['OEM'] = (
            dummy['TOYO/COMP'] + '|' + dummy['BRAND']
        ).apply(lambda x: 'toyota' if 'toyota|' in x else x.split('|')[-1]).apply(
            lambda x: x.replace('_', ' ').upper()
        )
        dummy.drop(['BRAND', 'TOYO/COMP'], axis=1, inplace=True)

        return dummy.groupby(dummy['OEM']).sum().drop(['OEM'], axis=1)

    @staticmethod
    def _add_p(grouped_ptdf: pdDataFrame, pt_type: str) -> pdDataFrame:
        pt_type = pt_type.upper()
        for col in grouped_ptdf:
            grouped_ptdf[col + ' US ' + pt_type + ' SALES %'] = (
                (grouped_ptdf[col] / grouped_ptdf[col].sum()) * 100
            )
        return grouped_ptdf

    def sales_percentages(self) -> pdDataFrame:
        sales = self.frames['sales'].copy()
        s10 = sales.loc[:, [c for c in sales.columns if int(c[3:]) > 2009]].copy()
        for col in s10:
            s10[col + ' US MARKET SHARE'] = (
                (s10.loc[[r for r in s10.index if 'INDUSTRY' not in r], col] 
                / s10.loc['INDUSTRY SALES', col]) * 100
            )
        return s10

    def oem_percentages(self, pt: str) -> pdDataFrame:
        dummy = self.frames[pt].copy()
        grouped = _group_brands(dummy)
        return _add_p(grouped, pt)


