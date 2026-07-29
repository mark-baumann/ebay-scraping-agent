"""Tests für eBay Scraping Agent."""

import pytest
import json
import os
import tempfile
from ebay_scraper import EbayProduct, EbayScraper, PriceAlert


# ═══════════════════════════════════════════════════════════════
# EbayProduct
# ═══════════════════════════════════════════════════════════════

class TestEbayProduct:
    def test_creation_defaults(self):
        p = EbayProduct("Test Artikel", 10.0)
        assert p.title == "Test Artikel"
        assert p.price == 10.0
        assert p.currency == "EUR"
        assert p.condition == "Gebraucht"
        assert p.shipping == 0.0
        assert p.url == ""
        assert p.seller == ""
        assert p.location == "Deutschland"
        assert p.scraped_at is not None

    def test_creation_full(self):
        p = EbayProduct(
            title="MacBook Pro",
            price=1299.99,
            currency="EUR",
            condition="Neu",
            shipping=5.99,
            url="https://ebay.de/mbp",
            seller="apple-store",
            location="Berlin"
        )
        assert p.title == "MacBook Pro"
        assert p.price == 1299.99
        assert p.condition == "Neu"
        assert p.shipping == 5.99
        assert p.url == "https://ebay.de/mbp"
        assert p.seller == "apple-store"
        assert p.location == "Berlin"

    def test_scraped_at_is_isoformat(self):
        p = EbayProduct("Test", 1.0)
        # ISO-Format enthält 'T'
        assert "T" in p.scraped_at


# ═══════════════════════════════════════════════════════════════
# EbayScraper
# ═══════════════════════════════════════════════════════════════

class TestEbayScraper:
    def test_init(self):
        s = EbayScraper(headless=True)
        assert s.headless is True
        assert s.products == []

    def test_init_headless_false(self):
        s = EbayScraper(headless=False)
        assert s.headless is False

    @pytest.mark.asyncio
    async def test_search_returns_empty_list(self):
        """search() ist ein Stub und gibt leere Liste zurück."""
        s = EbayScraper()
        result = await s.search("iPhone 15", max_pages=2)
        assert result == []
        assert s.products == []


class TestEbayScraperAnalysis:
    def test_analyze_prices_empty(self):
        s = EbayScraper()
        result = s.analyze_prices()
        assert result == {"error": "Keine Produkte gesammelt"}

    def test_analyze_prices_no_valid_prices(self):
        s = EbayScraper()
        s.products = [EbayProduct("Gratis", 0.0)]
        result = s.analyze_prices()
        assert result == {"error": "Keine gültigen Preise"}

    def test_analyze_prices_single(self):
        s = EbayScraper()
        s.products = [EbayProduct("A", 100.0)]
        result = s.analyze_prices()
        assert result["count"] == 1
        assert result["min"] == 100.0
        assert result["max"] == 100.0
        assert result["avg"] == 100.0
        assert result["median"] == 100.0

    def test_analyze_prices_multiple(self):
        s = EbayScraper()
        s.products = [
            EbayProduct("A", 10.0),
            EbayProduct("B", 20.0),
            EbayProduct("C", 30.0),
        ]
        result = s.analyze_prices()
        assert result["count"] == 3
        assert result["min"] == 10.0
        assert result["max"] == 30.0
        assert result["avg"] == 20.0
        assert result["median"] == 20.0

    def test_analyze_prices_even_count_median(self):
        """Median bei gerader Anzahl: Mittelwert der beiden mittleren Werte."""
        s = EbayScraper()
        s.products = [
            EbayProduct("A", 10.0),
            EbayProduct("B", 20.0),
            EbayProduct("C", 30.0),
            EbayProduct("D", 40.0),
        ]
        result = s.analyze_prices()
        assert result["count"] == 4
        assert result["median"] == 25.0  # (20 + 30) / 2

    def test_analyze_prices_skips_zero(self):
        """Preise von 0 werden ignoriert."""
        s = EbayScraper()
        s.products = [
            EbayProduct("A", 0.0),
            EbayProduct("B", 50.0),
            EbayProduct("C", 100.0),
        ]
        result = s.analyze_prices()
        assert result["count"] == 2
        assert result["min"] == 50.0
        assert result["max"] == 100.0

    def test_analyze_prices_unsorted_input(self):
        """Median funktioniert auch bei unsortierten Eingaben."""
        s = EbayScraper()
        s.products = [
            EbayProduct("A", 50.0),
            EbayProduct("B", 10.0),
            EbayProduct("C", 30.0),
        ]
        result = s.analyze_prices()
        assert result["median"] == 30.0


class TestEbayScraperExport:
    def test_export_json(self):
        s = EbayScraper()
        s.products = [
            EbayProduct("Test", 42.0, seller="test-shop"),
        ]
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            s.export_json(path)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            assert len(data) == 1
            assert data[0]["title"] == "Test"
            assert data[0]["price"] == 42.0
            assert data[0]["seller"] == "test-shop"
        finally:
            os.unlink(path)

    def test_export_csv(self):
        s = EbayScraper()
        s.products = [
            EbayProduct("Test", 42.0, seller="test-shop"),
        ]
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            s.export_csv(path)
            with open(path, encoding="utf-8") as f:
                content = f.read()
            assert "Test" in content
            assert "42.0" in content
            assert "test-shop" in content
        finally:
            os.unlink(path)

    def test_export_csv_empty(self):
        """CSV-Export mit leeren Produkten wirft keinen Fehler."""
        s = EbayScraper()
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            s.export_csv(path)  # sollte nicht crashen
        finally:
            os.unlink(path)


# ═══════════════════════════════════════════════════════════════
# PriceAlert
# ═══════════════════════════════════════════════════════════════

class TestPriceAlert:
    def test_init_default_threshold(self):
        alert = PriceAlert()
        assert alert.threshold == 10.0
        assert alert.watchlist == []

    def test_init_custom_threshold(self):
        alert = PriceAlert(threshold_percent=5.0)
        assert alert.threshold == 5.0

    def test_add_watch(self):
        alert = PriceAlert()
        product = EbayProduct("iPhone 15", 699.0)
        alert.add_watch(product, target_price=600.0)
        assert len(alert.watchlist) == 1
        assert alert.watchlist[0]["target_price"] == 600.0
        assert alert.watchlist[0]["product"]["title"] == "iPhone 15"
        assert "added_at" in alert.watchlist[0]

    def test_check_alerts_below_target(self):
        alert = PriceAlert()
        product = EbayProduct("iPhone 15", 699.0)
        alert.add_watch(product, target_price=600.0)
        
        # Aktueller Preis ist unter Zielpreis
        current = [EbayProduct("iPhone 15", 550.0)]
        alerts = alert.check_alerts(current)
        assert len(alerts) == 1
        assert alerts[0]["current_price"] == 550.0
        assert alerts[0]["target_price"] == 600.0
        assert alerts[0]["savings"] == 50.0

    def test_check_alerts_above_target(self):
        alert = PriceAlert()
        product = EbayProduct("iPhone 15", 699.0)
        alert.add_watch(product, target_price=600.0)
        
        # Aktueller Preis ist über Zielpreis
        current = [EbayProduct("iPhone 15", 650.0)]
        alerts = alert.check_alerts(current)
        assert len(alerts) == 0

    def test_check_alerts_exact_match(self):
        alert = PriceAlert()
        product = EbayProduct("iPhone 15", 699.0)
        alert.add_watch(product, target_price=600.0)
        
        current = [EbayProduct("iPhone 15", 600.0)]
        alerts = alert.check_alerts(current)
        assert len(alerts) == 1
        assert alerts[0]["savings"] == 0.0

    def test_check_alerts_no_match(self):
        alert = PriceAlert()
        product = EbayProduct("iPhone 15", 699.0)
        alert.add_watch(product, target_price=600.0)
        
        # Anderes Produkt
        current = [EbayProduct("Samsung Galaxy", 500.0)]
        alerts = alert.check_alerts(current)
        assert len(alerts) == 0

    def test_check_alerts_case_insensitive(self):
        alert = PriceAlert()
        product = EbayProduct("iPhone 15", 699.0)
        alert.add_watch(product, target_price=600.0)
        
        current = [EbayProduct("iphone 15", 550.0)]
        alerts = alert.check_alerts(current)
        assert len(alerts) == 1

    def test_multiple_watches(self):
        alert = PriceAlert()
        alert.add_watch(EbayProduct("A", 100.0), target_price=80.0)
        alert.add_watch(EbayProduct("B", 200.0), target_price=150.0)
        
        current = [
            EbayProduct("A", 70.0),
            EbayProduct("B", 160.0),
        ]
        alerts = alert.check_alerts(current)
        assert len(alerts) == 1  # Nur A ist unter Zielpreis
        assert alerts[0]["product"] == "A"
