import re
import pandas as pd
from datetime import datetime
from dataclasses import (
    dataclass,
    field,
)
from typing import (
    List,
    TypeVar,
    Tuple,
)

from AFV.redim_sheet import *  # contains 3 xw TypeVars & SheetDims class

# custom object types
pdDataFrame = TypeVar('pd.main.frame.DataFrame')
pdSeries = TypeVar('pd.core.series.Series')

@dataclass
class _FlippedClean:
    totals: xwSheet = field(repr=False)

    def __post_init__(self):
        t_dims = SheetDims(totals).digest_add
        self.flip = pd.DataFrame(totals[t_dims].value).transpose()
        self.flip.rename(columns=self._first_row_to_cols(), inplace=True)
        self.flip.drop(0, inplace=True)


        self.shinychrome = self.clean_up()


    def _first_row_to_cols(self) -> pdDataFrame:
        return self.flipDF.iloc[0, :].fillna(
            {i: 'LEVEL_' + str(i) for i in range(4)}
        ).replace({'Year': 'LEVEL_3'})

    def _clean_3(self) -> pdSeries:
        c3 = flip['LEVEL_3'].copy()
        c3.fillna(flip['LEVEL_2'], inplace=True)
        c3.fillna(flip['LEVEL_1'], inplace=True)
        return c3

    def _clean_2(self) -> pdSeries:
        c2 = flip['LEVEL_2'].copy()
        c2.fillna(flip['LEVEL_1'], inplace=True)
        c2.fillna(method='ffill', inplace=True)
        return c2

    def _clean_1(self) -> pdSeries:
        c1 = flip['LEVEL_1'].copy()
        return c1.fillna(method='ffill', inplace=True)

    def _clean_0(self) -> pdSeries:
        c0 = flip['LEVLE_0'].copy()
        return c0.fillna(method='ffill', inplace=True)

    @staticmethod
    def define_blanks(sers: List[pdSeries]) -> Tuple[pdSeries]:
        return tuple(s.fillna('(blank)', inplace=True) for s in sers)

    @staticmethod
    def clean_shinies(sers: Tuple[pdSeries]) -> Tuple[pdSeries]:
        return tuple(
            s.apply(lambda x: '_'.join(x.lower().strip().split())) for s in sers
        )

    @staticmethod
    def fix_subie(clean2: pdSeries) -> pdSeries:
        return clean2.apply(lambda x: x if 'subaru' not in x else 'subaru')

    @staticmethod
    def rename_pt_type(clean0: pdSeries) -> pdSeries:
        return clean0.apply(
            lambda x: x
                .replace('fuel_cell_vehicles', 'fcev')
                .replace('plug-in_hybrids', 'phev')
                .replace('hybrids', 'hev')
                .replace('electric_vehicles', 'bev')
        )

    def cat_flip(self, sers: List[pdSeries]) -> pdDataFrame:
        new_flip = self.flip.copy()
        for ser in sers:
            new_flip.concat(ser, axis=1)

        return new_flip

    # cat into df first before doing the rest
    @staticmethod
    def clean_phev(new_flip: pdDataFrame) -> pdDataFrame:
        new2 = new_flip.copy()

        new2.loc[
            (new2['CLEAN_0'] == 'phev')
            & (~new2['CLEAN_2'].isin(
                    ['non-fleet', 'fleet', 'total_us_(no_hawaii)', 'hawaii',]
                )
            )
            & (new2['CLEAN_2'] == 'total_us_prius_plug-in'),
            'CLEAN_1',
        ] = 'toyota'

        new2.loc[
            (new2['CLEAN_0'] == 'phev')
            & (~new2['CLEAN_2'].isin(
                    ['non-fleet','fleet','total_us_(no_hawaii)','hawaii',]
                )
            )
            & (new2['CLEAN_2'] != 'total_us_prius_plug-in')
            & (
                (~new2['CLEAN_2'].str.contains('sales'))
                & (~new2['CLEAN_2'].str.contains('share'))
            ),
            'CLEAN_1',
        ]
        return new2

    @staticmethod
    def clean_bev(new_flip: pdDataFrame) -> pdDataFrame:
        new2 = new_flip.copy()
        new2.loc[
            (new2['CLEAN_0'] == 'bev')
            & (new2['CLEAN_2'] == 'toyota'),
            'CLEAN_1',
        ] = 'toyota'
        
        new2.loc[
            (new2['CLEAN_0'] == 'bev')
            & (new2['CLEAN_2'] != 'toyota')
            & (new2['LEVEL_1'].isna()),
            'CLEAN_1',
        ] = 'competitor'
        return new2

    def clean_up(self) -> pdDataFrame:
        c3 = self._clean_3()
        c2 = self._clean_2()
        c1 = self._clean_1()
        c0 = self._clean_0()
        shinies = define_blanks([c0, c1, c2, c3])
        (s0, s1, s2, s3) = clean_shinies(shinies)
        s2 = fix_subie(s2)
        s0 = rename_pt_type(s0)
        chrome = cat_flip([s0, s1, s2, s3])
        shiny = clean_phev(chrome)
        shiny_and_chrome = clean_bev(shiny)
        shiny_and_chrome['CLEAN_1'] = shiny_and_chrome['CLEAN_1'].apply(
            lambda x: x if x != 'toyota_/_lexus' else 'toyota'
        )
        return shiny_and_chrome


    

