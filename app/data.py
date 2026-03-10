from datetime import datetime, timedelta
import random
from typing import List, Optional
from pydantic import BaseModel

# Stock models
class StockQuote(BaseModel):
    date: str
    time: str
    isin: str
    price: float
    index_name: str


class StockData:
    # 5 Danish stocks with ISINs
    STOCKS = [
        {"isin": "DK0060635560", "name": "Novo Nordisk", "index": "OMX20"},
        {"isin": "DK0010268606", "name": "Danske Bank", "index": "OMX20"},
        {"isin": "DK0010244508", "name": "DSV Panalpina", "index": "OMX20"},
        {"isin": "DK0010292332", "name": "Chr. Hansen", "index": "MidCap"},
        {"isin": "DK0010249390", "name": "Orsted", "index": "OMX20"}
    ]

    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        self.quotes: List[StockQuote] = []
        self._generate_quotes()

    def _generate_quotes(self):
        """Generate random stock quotes for the past 30 days"""
        base_date = datetime.now() - timedelta(days=30)

        for day_offset in range(30):
            current_date = base_date + timedelta(days=day_offset)

            for stock in self.STOCKS:
                # Generate 5 quotes per day per stock
                for quote_num in range(5):
                    hour = 9 + (quote_num * 2)  # 9 AM, 11 AM, 1 PM, 3 PM, 5 PM
                    minute = random.randint(0, 59)

                    # Generate random price (between 100 and 500 DKK)
                    price = round(random.uniform(100, 500), 2)

                    quote = StockQuote(
                        date=current_date.strftime("%Y-%m-%d"),
                        time=f"{hour:02d}:{minute:02d}",
                        isin=stock["isin"],
                        price=price,
                        index_name=stock["index"]
                    )
                    self.quotes.append(quote)

    def get_all_quotes(self) -> List[StockQuote]:
        """Get all quotes"""
        return self.quotes

    def filter_quotes(
        self,
        index_name: Optional[str] = None,
        date: Optional[str] = None
    ) -> List[StockQuote]:
        """Filter quotes by index name and/or date"""
        filtered = self.quotes

        if index_name:
            filtered = [q for q in filtered if q.index_name == index_name]

        if date:
            filtered = [q for q in filtered if q.date == date]

        return filtered

    def get_unique_dates(self) -> List[str]:
        """Get list of unique dates"""
        return sorted(set(q.date for q in self.quotes))

    def get_unique_indices(self) -> List[str]:
        """Get list of unique index names"""
        return sorted(set(q.index_name for q in self.quotes))
