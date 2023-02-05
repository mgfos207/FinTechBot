from  dataclasses import dataclass

@dataclass
class Stocks:
    _symbol: str
    _stock_info: dict
    _price_info: dict