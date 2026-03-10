import pytest
from datetime import datetime, timedelta
from app.data import StockData, StockQuote
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Fixture to provide TestClient"""
    return TestClient(app)


class TestStockData:
    """Test the StockData class"""

    def test_stock_data_initialization(self):
        """Test that StockData initializes correctly"""
        stock_data = StockData(seed=42)
        assert stock_data is not None
        assert len(stock_data.quotes) > 0

    def test_stock_data_has_5_isins(self):
        """Test that data contains exactly 5 different ISINs"""
        stock_data = StockData(seed=42)
        isins = set(q.isin for q in stock_data.quotes)
        assert len(isins) == 5

    def test_stock_data_has_30_days(self):
        """Test that data spans 30 days"""
        stock_data = StockData(seed=42)
        dates = set(q.date for q in stock_data.quotes)
        assert len(dates) == 30

    def test_stock_quote_structure(self):
        """Test that StockQuote has correct structure"""
        stock_data = StockData(seed=42)
        quote = stock_data.quotes[0]

        assert hasattr(quote, 'date')
        assert hasattr(quote, 'time')
        assert hasattr(quote, 'isin')
        assert hasattr(quote, 'price')
        assert hasattr(quote, 'index_name')

        # Validate types
        assert isinstance(quote.date, str)
        assert isinstance(quote.time, str)
        assert isinstance(quote.isin, str)
        assert isinstance(quote.price, float)
        assert isinstance(quote.index_name, str)

    def test_price_range(self):
        """Test that prices are within expected range"""
        stock_data = StockData(seed=42)
        for quote in stock_data.quotes:
            assert 100 <= quote.price <= 500

    def test_date_format(self):
        """Test that dates are in correct format"""
        stock_data = StockData(seed=42)
        for quote in stock_data.quotes:
            try:
                datetime.strptime(quote.date, "%Y-%m-%d")
            except ValueError:
                pytest.fail(f"Invalid date format: {quote.date}")

    def test_time_format(self):
        """Test that times are in correct format"""
        stock_data = StockData(seed=42)
        for quote in stock_data.quotes:
            try:
                datetime.strptime(quote.time, "%H:%M")
            except ValueError:
                pytest.fail(f"Invalid time format: {quote.time}")

    def test_isin_format(self):
        """Test that ISINs are in expected format"""
        stock_data = StockData(seed=42)
        expected_isins = {
            "DK0060635560", "DK0010268606", "DK0010244508",
            "DK0010292332", "DK0010249390"
        }
        actual_isins = set(q.isin for q in stock_data.quotes)
        assert actual_isins == expected_isins

    def test_filter_by_index_name(self):
        """Test filtering by index name"""
        stock_data = StockData(seed=42)
        filtered = stock_data.filter_quotes(index_name="OMX20")

        assert len(filtered) > 0
        for quote in filtered:
            assert quote.index_name == "OMX20"

    def test_filter_by_date(self):
        """Test filtering by date"""
        stock_data = StockData(seed=42)
        all_dates = stock_data.get_unique_dates()
        test_date = all_dates[0]

        filtered = stock_data.filter_quotes(date=test_date)

        assert len(filtered) > 0
        for quote in filtered:
            assert quote.date == test_date

    def test_filter_by_index_and_date(self):
        """Test filtering by both index name and date"""
        stock_data = StockData(seed=42)
        all_dates = stock_data.get_unique_dates()
        test_date = all_dates[0]

        filtered = stock_data.filter_quotes(index_name="OMX20", date=test_date)

        if len(filtered) > 0:
            for quote in filtered:
                assert quote.index_name == "OMX20"
                assert quote.date == test_date

    def test_filter_with_empty_results(self):
        """Test filtering that returns no results"""
        stock_data = StockData(seed=42)
        filtered = stock_data.filter_quotes(index_name="NONEXISTENT")
        assert len(filtered) == 0

    def test_get_unique_dates(self):
        """Test getting unique dates"""
        stock_data = StockData(seed=42)
        dates = stock_data.get_unique_dates()

        assert len(dates) == 30
        assert all(isinstance(d, str) for d in dates)
        # Check that dates are sorted
        assert dates == sorted(dates)

    def test_get_unique_indices(self):
        """Test getting unique indices"""
        stock_data = StockData(seed=42)
        indices = stock_data.get_unique_indices()

        assert len(indices) >= 2  # We have OMX20 and MidCap
        assert "OMX20" in indices
        assert "MidCap" in indices
        # Check that indices are sorted
        assert indices == sorted(indices)

    def test_get_all_quotes(self):
        """Test getting all quotes"""
        stock_data = StockData(seed=42)
        all_quotes = stock_data.get_all_quotes()

        assert len(all_quotes) > 0
        assert all(isinstance(q, StockQuote) for q in all_quotes)

    def test_reproducible_data_with_seed(self):
        """Test that same seed produces same data"""
        stock_data1 = StockData(seed=42)
        stock_data2 = StockData(seed=42)

        assert len(stock_data1.quotes) == len(stock_data2.quotes)
        for q1, q2 in zip(stock_data1.quotes, stock_data2.quotes):
            assert q1.date == q2.date
            assert q1.time == q2.time
            assert q1.isin == q2.isin
            assert q1.price == q2.price


class TestFastAPIEndpoints:
    """Test FastAPI endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_get_root(self, client):
        """Test root endpoint returns HTML"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Danish Stock Exchange" in response.text

    def test_get_quotes_all(self, client):
        """Test getting all quotes"""
        response = client.get("/api/quotes")
        assert response.status_code == 200
        quotes = response.json()
        assert len(quotes) > 0
        assert all("date" in q for q in quotes)
        assert all("time" in q for q in quotes)
        assert all("isin" in q for q in quotes)
        assert all("price" in q for q in quotes)

    def test_get_quotes_filter_by_index(self, client):
        """Test filtering quotes by index name"""
        response = client.get("/api/quotes?index_name=OMX20")
        assert response.status_code == 200
        quotes = response.json()
        assert len(quotes) > 0
        assert all(q["index_name"] == "OMX20" for q in quotes)

    def test_get_quotes_filter_by_date(self, client):
        """Test filtering quotes by date"""
        # First get all quotes to find a valid date
        response = client.get("/api/dates")
        dates = response.json()
        test_date = dates[0]

        response = client.get(f"/api/quotes?date={test_date}")
        assert response.status_code == 200
        quotes = response.json()
        assert len(quotes) > 0
        assert all(q["date"] == test_date for q in quotes)

    def test_get_quotes_filter_by_index_and_date(self, client):
        """Test filtering quotes by both index and date"""
        response = client.get("/api/dates")
        dates = response.json()
        test_date = dates[0]

        response = client.get(f"/api/quotes?index_name=OMX20&date={test_date}")
        assert response.status_code == 200
        quotes = response.json()

        if len(quotes) > 0:
            assert all(q["index_name"] == "OMX20" for q in quotes)
            assert all(q["date"] == test_date for q in quotes)

    def test_get_quotes_invalid_filter(self, client):
        """Test filtering with non-existent values"""
        response = client.get("/api/quotes?index_name=NONEXISTENT")
        assert response.status_code == 200
        quotes = response.json()
        assert len(quotes) == 0

    def test_get_dates(self, client):
        """Test getting available dates"""
        response = client.get("/api/dates")
        assert response.status_code == 200
        dates = response.json()
        assert len(dates) == 30
        assert all(isinstance(d, str) for d in dates)

    def test_get_indices(self, client):
        """Test getting available indices"""
        response = client.get("/api/indices")
        assert response.status_code == 200
        indices = response.json()
        assert len(indices) >= 2
        assert "OMX20" in indices

    def test_response_model_validation(self, client):
        """Test that response models are validated"""
        response = client.get("/api/quotes")
        assert response.status_code == 200
        quotes = response.json()

        for quote in quotes[:5]:  # Check first 5 quotes
            assert "date" in quote
            assert "time" in quote
            assert "isin" in quote
            assert "price" in quote
            assert "index_name" in quote

            # Validate types
            assert isinstance(quote["date"], str)
            assert isinstance(quote["time"], str)
            assert isinstance(quote["isin"], str)
            assert isinstance(quote["price"], (int, float))
            assert isinstance(quote["index_name"], str)
