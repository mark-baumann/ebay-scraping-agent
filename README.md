# 🛒 eBay Scraping Agent

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Browser-Use](https://img.shields.io/badge/Browser--Use-Automation-green.svg)](https://github.com/browser-use/browser-use)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red.svg)](https://streamlit.io/)

**Automatisierte eBay-Produktsuche & Preisanalyse** — Browser-Use-basierter Agent zum Durchsuchen von eBay, Extrahieren von Produktdaten und Preisvergleich.

## 📋 Beschreibung

Dieser Agent automatisiert die eBay-Produktsuche mithilfe von Browser-Use. Er navigiert eigenständig durch eBay-Suchergebnisse, extrahiert strukturierte Produktdaten (Titel, Preis, Zustand, Versand, Verkäufer) und bietet eine interaktive Streamlit-Oberfläche für Preisanalyse, Visualisierung und Preisalarme.

- **Browser-Automation** — Browser-Use-gesteuerte eBay-Navigation
- **Strukturierte Extraktion** — Produktdaten als `EbayProduct`-Dataclass
- **Preisanalyse** — Statistiken, Preisverteilung, Deal-Erkennung
- **Export** — JSON- und CSV-Export der Ergebnisse

## ✨ Features

- 🔍 **Automatisierte Suche** — eBay.de nach beliebigen Suchbegriffen durchsuchen
- 📊 **Preisanalyse** — Min/Max/Median, Preisverteilung, Versandkosten-Analyse
- 🏷️ **Zustandserkennung** — Neu, Gebraucht, Generalüberholt
- 📍 **Standort-Info** — Verkäuferstandort extrahieren
- 💰 **Deal-Finder** — Produkte unter Durchschnittspreis identifizieren
- 📈 **Preisalarme** — Schwellwert-basierte Benachrichtigungen
- 🖥️ **Streamlit-App** — Interaktive Suche, Filter, Visualisierung
- 📦 **Export** — Ergebnisse als JSON/CSV speichern
- 🧪 **Test-Suite** — pytest-Tests für Scraper und App

## 🚀 Installation

```bash
# Repository klonen
git clone https://github.com/mark-baumann/ebay-scraping-agent.git
cd ebay-scraping-agent

# Virtuelle Umgebung erstellen
python3 -m venv .venv
source .venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Browser-Use installieren
pip install browser-use
playwright install chromium
```

## 🎮 Nutzung

### Streamlit-App

```bash
streamlit run app.py
```

Die App bietet:
- **Produktsuche** — Suchbegriff eingeben, Ergebnisseite analysieren
- **Preisanalyse** — Statistische Auswertung mit Charts
- **Preisalarme** — Schwellwerte definieren und überwachen
- **Export** — Ergebnisse als CSV/JSON herunterladen

### CLI-Scraper

```bash
# Einfache Suche
python ebay_scraper.py --search "iPhone 15"

# Mit mehreren Seiten
python ebay_scraper.py --search "MacBook Pro" --max-pages 5

# Ergebnisse als JSON speichern
python ebay_scraper.py --search "Grafikkarte" --output results.json
```

### Tests

```bash
pytest tests/ -v
```

## 🏗️ Tech-Stack

| Komponente | Technologie |
|---|---|
| **Sprache** | Python 3.10+ |
| **Automation** | Browser-Use, Playwright |
| **Daten** | Pandas, NumPy |
| **UI** | Streamlit |
| **Testing** | pytest |

## 📁 Projektstruktur

```
ebay-scraping-agent/
├── ebay_scraper.py         # Kern-Scraper mit EbayProduct-Dataclass
├── app.py                  # Streamlit-App mit Preisanalyse
├── pyproject.toml          # Projekt-Konfiguration
├── .gitignore
└── tests/
    ├── __init__.py
    └── test_ebay_scraper.py
```

## 👤 Autor

**Mark Baumann** — [GitHub](https://github.com/mark-baumann)

---

*Für Fragen oder Beiträge: Issue erstellen oder Pull Request öffnen.*
