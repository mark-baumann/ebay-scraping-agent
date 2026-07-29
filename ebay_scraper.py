"""
eBay Scraping Agent — Automatisierte Produktsuche & Preisanalyse
================================================================
Browser-Use-basierter Agent zum Durchsuchen von eBay,
Extrahieren von Produktdaten und Preisvergleich.

Nutzung:
    python ebay_scraper.py --search "iPhone 15" --max-pages 3
"""

import asyncio
import json
import argparse
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class EbayProduct:
    """Strukturierte eBay-Produktdaten."""
    title: str
    price: float
    currency: str = "EUR"
    condition: str = "Gebraucht"
    shipping: float = 0.0
    url: str = ""
    seller: str = ""
    location: str = "Deutschland"
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())


class EbayScraper:
    """
    eBay-Scraper mit Browser-Use.
    
    Extrahiert Produktdaten aus eBay-Suchergebnissen
    und speichert sie strukturiert als JSON/CSV.
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.products: List[EbayProduct] = []
    
    async def search(self, query: str, max_pages: int = 3) -> List[EbayProduct]:
        """
        Durchsucht eBay nach Produkten.
        
        Args:
            query: Suchbegriff (z.B. "iPhone 15")
            max_pages: Maximale Anzahl Ergebnisseiten
        
        Returns:
            Liste von EbayProduct-Objekten
        """
        # Browser-Use Agent Task
        task = f"""
        Gehe auf ebay.de und suche nach "{query}".
        Extrahiere für jedes Produkt auf den ersten {max_pages} Seiten:
        - Titel
        - Preis (als Zahl)
        - Zustand (Neu/Gebraucht)
        - Versandkosten
        - Verkäufer-Name
        - Artikel-URL
        
        Speichere die Daten als JSON.
        """
        
        # TODO: Browser-Use Integration
        # from browser_use import Agent, ChatBrowserUse
        # agent = Agent(task=task, llm=ChatBrowserUse())
        # result = await agent.run()
        
        print(f"🔍 Suche nach: {query}")
        print(f"📄 Max. Seiten: {max_pages}")
        print("⚠️  Browser-Use Integration pending — installiere browser-use")
        
        return self.products
    
    def analyze_prices(self) -> dict:
        """
        Analysiert die gesammelten Preisdaten.
        
        Returns:
            Dict mit Preisstatistiken
        """
        if not self.products:
            return {"error": "Keine Produkte gesammelt"}
        
        prices = [p.price for p in self.products if p.price > 0]
        
        if not prices:
            return {"error": "Keine gültigen Preise"}
        
        sorted_prices = sorted(prices)
        n = len(sorted_prices)
        if n % 2 == 0:
            median = (sorted_prices[n // 2 - 1] + sorted_prices[n // 2]) / 2
        else:
            median = sorted_prices[n // 2]
        
        return {
            "count": n,
            "min": min(prices),
            "max": max(prices),
            "avg": sum(prices) / n,
            "median": median,
        }
    
    def export_json(self, path: str = "ebay_products.json"):
        """Exportiert Produkte als JSON."""
        data = [p.__dict__ for p in self.products]
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"📦 {len(self.products)} Produkte → {path}")
    
    def export_csv(self, path: str = "ebay_products.csv"):
        """Exportiert Produkte als CSV."""
        import csv
        if not self.products:
            return
        
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.products[0].__dict__.keys())
            writer.writeheader()
            for p in self.products:
                writer.writerow(p.__dict__)
        print(f"📊 {len(self.products)} Produkte → {path}")


class PriceAlert:
    """
    Preisalarm-System.
    
    Überwacht Produkte und benachrichtigt bei Preisänderungen.
    """
    
    def __init__(self, threshold_percent: float = 10.0):
        self.threshold = threshold_percent
        self.watchlist: List[dict] = []
    
    def add_watch(self, product: EbayProduct, target_price: float):
        """Fügt ein Produkt zur Watchlist hinzu."""
        self.watchlist.append({
            "product": product.__dict__,
            "target_price": target_price,
            "added_at": datetime.now().isoformat()
        })
    
    def check_alerts(self, current_products: List[EbayProduct]) -> List[dict]:
        """
        Prüft ob Preise unter den Schwellwert gefallen sind.
        
        Returns:
            Liste von Alert-Dicts
        """
        alerts = []
        for watch in self.watchlist:
            for product in current_products:
                if product.title.lower() == watch["product"]["title"].lower():
                    if product.price <= watch["target_price"]:
                        alerts.append({
                            "product": product.title,
                            "current_price": product.price,
                            "target_price": watch["target_price"],
                            "savings": watch["target_price"] - product.price,
                            "url": product.url
                        })
        return alerts


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

async def main():
    parser = argparse.ArgumentParser(description="eBay Scraping Agent")
    parser.add_argument("--search", type=str, help="Suchbegriff")
    parser.add_argument("--max-pages", type=int, default=3)
    parser.add_argument("--export", type=str, default="json", 
                       choices=["json", "csv", "both"])
    
    args = parser.parse_args()
    
    scraper = EbayScraper(headless=True)
    
    if args.search:
        products = await scraper.search(args.search, args.max_pages)
        
        # Demo-Daten für Test
        if not products:
            demo = [
                EbayProduct("iPhone 15 128GB", 699.0, "EUR", "Neu", 0.0, 
                           "https://ebay.de/example1", "top-seller"),
                EbayProduct("iPhone 15 128GB", 599.0, "EUR", "Gebraucht", 4.99,
                           "https://ebay.de/example2", "private-seller"),
                EbayProduct("iPhone 15 Pro 256GB", 899.0, "EUR", "Neu", 0.0,
                           "https://ebay.de/example3", "electronics-store"),
            ]
            scraper.products = demo
            print(f"\n📊 Demo-Daten: {len(demo)} Produkte")
        
        # Analyse
        stats = scraper.analyze_prices()
        print(f"\n📈 Preisanalyse für '{args.search}':")
        print(f"   Anzahl: {stats.get('count', 0)}")
        print(f"   Min: {stats.get('min', 0):.2f} €")
        print(f"   Max: {stats.get('max', 0):.2f} €")
        print(f"   Durchschnitt: {stats.get('avg', 0):.2f} €")
        print(f"   Median: {stats.get('median', 0):.2f} €")
        
        # Export
        if args.export in ("json", "both"):
            scraper.export_json()
        if args.export in ("csv", "both"):
            scraper.export_csv()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
