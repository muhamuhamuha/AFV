import re
import xlwings as xw
import pandas as pd
from pathlib import Path
from datetime import datetime
from openpyxl.utils import (
    get_column_letter as col_letter
)
from dataclasses import (
    dataclass,
    field,
)
from typing import (
    List,
    Dict,
    TypeVar,
    Callable,
    Tuple,
)

from AFV.redim_sheet import *  # contains 3 xw TypeVars & UsedRange class

# custom object types
pdDataFrame = TypeVar('pd.main.frame.DataFrame')

def redefine_sheets(b: xwBook = xw.books.active) -> Dict[str, xwSheet]:
    return {s.name: s for s in b.sheets}


@dataclass
class CleanFlip:
    totals: xwSheet = field(repr=False)

    def __post_init__(self):
        t_dims = UsedRange(totals).digest_add
        self.flip = pd.DataFrame(totals[t_dims].value).transpose()
        self.flip.rename(columns=self._first_row_to_cols(), inplace=True)
        self.flip.drop(0, inplace=True)
        self.clean = self.clean_up()
        # there's also a self.clean_flip...


    def _first_row_to_cols(self) -> pdDataFrame:
        return self.flipDF.iloc[0, :].fillna(
            {i: 'LEVEL_' + str(i) for i in range(4)}
        ).replace({'Year': 'LEVEL_3'})

    def _clean_3(self) -> pdDataFrame:
        pass

    def _clean_2(self) -> pdDataFrame:
        pass

    def _clean_2(self) -> pdDataFrame:
        pass

    def define_blanks(self) -> pdDataFrame:
        pass

    def drop_total(self) -> pdDataFrame:
        pass

    def clean_shinies(self) -> pdDataFrame:
        pass

    def fix_subie(self) -> pdDataFrame:
        pass

    def rename_pt_type(self) -> pdDataFrame:
        pass

    def clean_phev(self) -> pdDataFrame:
        pass

    def clean_bev(self) -> pdDataFrame:
        pass

    def rename_toyolex(self) -> pdDataFrame:
        pass

    def clean_up(self) -> pdDataFrame:
        pass

