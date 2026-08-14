"""Application configuration and constants."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SAMPLE_DATA_PATH = DATA_DIR / "sample_portfolio.csv"

REQUIRED_COLUMNS = [
    "PolicyID",
    "CustomerID",
    "ProductLine",
    "Region",
    "Channel",
    "PolicyStartDate",
    "PolicyEndDate",
    "Exposure",
    "Premium",
    "ClaimCount",
    "ClaimAmount",
    "Age",
    "VehicleAge",
]

PRODUCT_LINES = ["Motor", "Home", "Commercial", "Liability"]
REGIONS = ["North", "South", "East", "West", "Central"]
CHANNELS = ["Agent", "Broker", "Direct", "Online"]

PAGE_OPTIONS = [
    "Home",
    "Data Upload",
    "Validation",
    "Cleaning",
    "Exploratory Analytics",
    "Frequency Modeling",
    "Severity Modeling",
    "Pure Premium",
    "Portfolio Analytics",
    "Executive Reporting",
]
