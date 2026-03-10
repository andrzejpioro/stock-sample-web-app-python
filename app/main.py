from fastapi import FastAPI, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional, List
from pathlib import Path

from app.data import StockData, StockQuote

# Setup paths
BASE_DIR = Path(__file__).parent

# Initialize FastAPI app
app = FastAPI(title="Danish Stock Exchange POC", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Initialize stock data once
stock_data = StockData()


@app.get("/api/quotes", response_model=List[StockQuote])
def get_quotes(
    index_name: Optional[str] = Query(None, description="Filter by index name"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)")
):
    """
    Get stock quotes with optional filtering

    - **index_name**: Optional filter by index (e.g., 'OMX20', 'MidCap')
    - **date**: Optional filter by date in YYYY-MM-DD format
    """
    return stock_data.filter_quotes(index_name=index_name, date=date)


@app.get("/api/dates", response_model=List[str])
def get_dates():
    """Get list of available dates"""
    return stock_data.get_unique_dates()


@app.get("/api/indices", response_model=List[str])
def get_indices():
    """Get list of available indices"""
    return stock_data.get_unique_indices()


@app.get("/")
def get_root(request: Request):
    """Serve the main HTML page using Jinja2 template"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
