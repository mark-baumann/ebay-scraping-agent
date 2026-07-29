# eBay Scraping Agent 🛒

Automatisierte eBay-Produktsuche & Preisanalyse mit [Browser-Use](https://github.com/browser-use/browser-use).

## Funktionen

- **Produktsuche**: Durchsucht eBay.de nach Artikeln
- **Preisanalyse**: Min, Max, Durchschnitt, Median
- **Export**: JSON und CSV
- **Preisalarm**: Watchlist mit Schwellwert-Benachrichtigungen

## Installation

```bash
uv sync
```

## Nutzung

```bash
# Suche mit JSON-Export
python ebay_scraper.py --search "iPhone 15" --max-pages 3 --export json

# Suche mit CSV-Export
python ebay_scraper.py --search "MacBook Pro" --export csv

# Beide Export-Formate
python ebay_scraper.py --search "Grafikkarte" --export both
```

## Tests

```bash
.venv/bin/python -m pytest -v
```

## Projektstruktur

```
ebay-scraping-agent/
├── ebay_scraper.py      # Hauptmodul: Scraper, Preisanalyse, CLI
├── tests/
│   └── test_ebay_scraper.py  # Unit-Tests
├── pyproject.toml       # Projekt-Konfiguration
└── README.md
```
