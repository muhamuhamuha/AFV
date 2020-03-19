import xlwings as xw
from dataclasses import (
    dataclass,
    field,
)
from typing import (
    TypeVar,
)

xwBook = TypeVar('xw.main.book')
xwSheet = TypeVar('xw.main.Sheet')
xwRange = TypeVar('xw.main.Range')

@dataclass
class UsedRange:
    sheet: xwSheet = field(repr=False)

    def __post_init__(self):
        self.down: xwRange = self.sheet['A1048576'].end('up')
        self.right: xwRange = self.sheet['XFD1'].end('left')
        self.bottomright: xwRange = self.right.offset(self.down.row - 1, 0)
        self.whole: xwRange = self.sheet['A1:' + self.bottomright.address]
        
    @property
    def down(self) -> xwRange:
        return self.down

    @property
    def right(self) -> xwRange:
        return self.right

    @property
    def bottomright(self) -> xwRange:
        return self.bottomright

    @property
    def whole(self) -> xwRange:
        return self.whole

    @property
    def d_row(self) -> str:
        return str(self.down.row)

    @property
    def r_row(self) -> str:
        return str(self.right.row)

    @property
    def br_row(self) -> str:
        return str(self.bottomright)

    @property
    def d_add(self) -> str:
        return self.down.address
    
    @property
    def r_add(self) -> str:
        return self.right.address

    @property
    def br_add(self) -> str:
        return self.bottomright.address

    @property
    def w_add(self) -> str:
        return self.whole.address


    
