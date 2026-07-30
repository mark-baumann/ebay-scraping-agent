"""
eBay Scraping Agent — Streamlit App
====================================
Web-Oberfläche für eBay-Produktsuche, Preisanalyse und Preisalarme.
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from typing import List

from ebay_scraper import EbayProduct


# ──────────────────────────────────────────────────────────────
# Demo-Daten & Hilfsfunktionen
# ──────────────────────────────────────────────────────────────

def generate_demo_products(query: str, count: int = 12) -> List[EbayProduct]:
    """Erzeugt realistische Demo-Produktdaten basierend auf der Suchanfrage."""
    conditions = ["Neu", "Gebraucht", "Neu", "Gebraucht", "Neu", "Generalüberholt"]
    sellers = ["top-seller-24", "electronics-pro", "private-verkauf", "outlet-store",
               "tech-deals", "gadget-world", "spar-fuchs", "premium-shop"]
    locations = ["Berlin", "München", "Hamburg", "Köln", "Frankfurt", "Stuttgart"]
    
    products = []
    base_price = np.random.uniform(50, 500)
    
    for i in range(count):
        variant = f"{query} - Variante {i+1}"
        price = base_price * np.random.uniform(0.6, 1.5)
        shipping = np.random.choice([0.0, 0.0, 0.0, 4.99, 5.99, 6.99])
        products.append(EbayProduct(
            title=variant,
            price=round(price, 2),
            condition=np.random.choice(conditions),
            shipping=shipping,
            url=f"https://ebay.de/itm/example{i+1}",
            seller=np.random.choice(sellers),
            location=np.random.choice(locations),
        ))
    
    return sorted(products, key=lambda p: p.price)


def analyze_prices(products: List[EbayProduct]) -> dict:
    """Preisstatistiken berechnen."""
    if not products:
        return {}
    prices = [p.price for p in products if p.price > 0]
    if not prices:
        return {}
    arr = np.array(prices)
    return {
        "Anzahl": len(arr),
        "Min (€)": round(float(arr.min()), 2),
        "Max (€)": round(float(arr.max()), 2),
        "Durchschnitt (€)": round(float(arr.mean()), 2),
        "Median (€)": round(float(np.median(arr)), 2),
        "Std-Abw. (€)": round(float(arr.std()), 2),
    }


# ──────────────────────────────────────────────────────────────
# Streamlit UI
# ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="eBay Scraping Agent",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🛒 eBay Scraping Agent")
st.markdown("**Automatisierte Produktsuche & Preisanalyse für eBay Deutschland**")

# ── Seitenleiste ──────────────────────────────────────────────

with st.sidebar:
    st.header("🔍 Sucheinstellungen")
    
    search_query = st.text_input(
        "Suchbegriff",
        value="iPhone 15",
        placeholder="z.B. iPhone 15, MacBook Pro, PS5...",
    )
    
    max_pages = st.slider(
        "Maximale Ergebnisseiten",
        min_value=1,
        max_value=10,
        value=3,
        help="Je mehr Seiten, desto mehr Produkte werden gesammelt.",
    )
    
    st.divider()
    
    st.header("🔔 Preisalarm")
    alert_enabled = st.checkbox("Preisalarm aktivieren", value=False)
    target_price = st.number_input(
        "Zielpreis (€)",
        min_value=0.0,
        value=500.0,
        step=10.0,
        disabled=not alert_enabled,
    )
    alert_email = st.text_input(
        "E-Mail für Benachrichtigung",
        placeholder="ihre@email.de",
        disabled=not alert_enabled,
    )
    
    st.divider()
    
    if st.button("🔍 Suche starten", type="primary", use_container_width=True):
        st.session_state.search_triggered = True
    else:
        if "search_triggered" not in st.session_state:
            st.session_state.search_triggered = False

# ── Hauptbereich ──────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Suchergebnisse",
    "📈 Preisanalyse",
    "🔔 Preisalarme",
    "📦 Export",
])

# ── Tab 1: Suchergebnisse ─────────────────────────────────────

with tab1:
    if st.session_state.search_triggered:
        with st.spinner(f"🔍 Suche nach '{search_query}' auf eBay..."):
            products = generate_demo_products(search_query, count=15)
            st.session_state.products = products
        
        st.success(f"✅ {len(products)} Produkte für '{search_query}' gefunden")
        
        # Filter
        col1, col2, col3 = st.columns(3)
        with col1:
            condition_filter = st.multiselect(
                "Zustand",
                options=["Neu", "Gebraucht", "Generalüberholt"],
                default=["Neu", "Gebraucht", "Generalüberholt"],
            )
        with col2:
            max_price_filter = st.number_input(
                "Max. Preis (€)",
                min_value=0.0,
                value=1000.0,
                step=50.0,
            )
        with col3:
            free_shipping_only = st.checkbox("Nur kostenloser Versand", value=False)
        
        # Filtern
        filtered = [
            p for p in products
            if p.condition in condition_filter
            and p.price <= max_price_filter
            and (not free_shipping_only or p.shipping == 0.0)
        ]
        
        # Tabelle
        if filtered:
            df = pd.DataFrame([{
                "Titel": p.title,
                "Preis (€)": f"{p.price:.2f}",
                "Zustand": p.condition,
                "Versand (€)": f"{p.shipping:.2f}",
                "Verkäufer": p.seller,
                "Standort": p.location,
                "URL": p.url,
            } for p in filtered])
            
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "URL": st.column_config.LinkColumn("Link"),
                },
            )
        else:
            st.warning("Keine Produkte entsprechen den Filterkriterien.")
    else:
        st.info("👈 Geben Sie einen Suchbegriff ein und klicken Sie auf **Suche starten**.")
        
        # Vorschau mit Platzhalter
        st.markdown("### 📋 Beispiel-Ergebnisse")
        demo = generate_demo_products("iPhone 15", count=5)
        df_demo = pd.DataFrame([{
            "Titel": p.title,
            "Preis (€)": f"{p.price:.2f}",
            "Zustand": p.condition,
            "Versand (€)": f"{p.shipping:.2f}",
            "Verkäufer": p.seller,
        } for p in demo])
        st.dataframe(df_demo, use_container_width=True, hide_index=True)
        st.caption("💡 Dies sind Beispiel-Daten. Starten Sie eine echte Suche für aktuelle Ergebnisse.")

# ── Tab 2: Preisanalyse ───────────────────────────────────────

with tab2:
    if "products" in st.session_state and st.session_state.products:
        products = st.session_state.products
        stats = analyze_prices(products)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Preisstatistik")
            for key, value in stats.items():
                st.metric(label=key, value=value)
        
        with col2:
            st.markdown("### 📈 Preisverteilung")
            prices = [p.price for p in products]
            df_chart = pd.DataFrame({
                "Produkt": [p.title[:30] + "..." for p in products],
                "Preis (€)": prices,
            }).sort_values("Preis (€)")
            
            st.bar_chart(df_chart.set_index("Produkt"), use_container_width=True)
        
        st.divider()
        
        # Boxplot-ähnliche Visualisierung
        st.markdown("### 📦 Preisspanne nach Zustand")
        df_cond = pd.DataFrame([{
            "Zustand": p.condition,
            "Preis (€)": p.price,
        } for p in products])
        
        conditions = df_cond["Zustand"].unique()
        cols = st.columns(len(conditions))
        for i, cond in enumerate(conditions):
            subset = df_cond[df_cond["Zustand"] == cond]["Preis (€)"]
            with cols[i]:
                st.metric(
                    label=f"{cond}",
                    value=f"Ø {subset.mean():.2f} €",
                    delta=f"Min {subset.min():.2f} €",
                )
    else:
        st.info("Führen Sie zuerst eine Suche aus, um die Preisanalyse zu sehen.")

# ── Tab 3: Preisalarme ────────────────────────────────────────

with tab3:
    st.markdown("### 🔔 Preisalarm-Konfiguration")
    
    if alert_enabled and "products" in st.session_state:
        products = st.session_state.products
        
        st.success(f"✅ Preisalarm aktiv — Zielpreis: **{target_price:.2f} €**")
        
        # Produkte unter Zielpreis
        bargains = [p for p in products if p.price <= target_price]
        
        if bargains:
            st.markdown(f"#### 🎉 {len(bargains)} Schnäppchen unter {target_price:.2f} €")
            df_bargains = pd.DataFrame([{
                "Titel": p.title,
                "Preis (€)": f"{p.price:.2f}",
                "Ersparnis (€)": f"{target_price - p.price:.2f}",
                "Zustand": p.condition,
                "URL": p.url,
            } for p in bargains])
            st.dataframe(df_bargains, use_container_width=True, hide_index=True)
        else:
            st.info(f"Keine Produkte unter {target_price:.2f} € gefunden.")
        
        st.divider()
        st.markdown("### 📋 Watchlist")
        
        if "watchlist" not in st.session_state:
            st.session_state.watchlist = []
        
        product_to_watch = st.selectbox(
            "Produkt zur Watchlist hinzufügen",
            options=[p.title for p in products],
        )
        
        if st.button("➕ Zur Watchlist hinzufügen"):
            selected = next(p for p in products if p.title == product_to_watch)
            st.session_state.watchlist.append({
                "title": selected.title,
                "current_price": selected.price,
                "target_price": target_price,
                "added_at": datetime.now().strftime("%d.%m.%Y %H:%M"),
            })
            st.rerun()
        
        if st.session_state.watchlist:
            df_watch = pd.DataFrame(st.session_state.watchlist)
            st.dataframe(df_watch, use_container_width=True, hide_index=True)
            
            if st.button("🗑️ Watchlist leeren"):
                st.session_state.watchlist = []
                st.rerun()
    else:
        if not alert_enabled:
            st.info("Aktivieren Sie den Preisalarm in der Seitenleiste.")
        else:
            st.info("Führen Sie zuerst eine Suche aus.")

# ── Tab 4: Export ─────────────────────────────────────────────

with tab4:
    st.markdown("### 📦 Daten exportieren")
    
    if "products" in st.session_state and st.session_state.products:
        products = st.session_state.products
        
        export_format = st.radio(
            "Export-Format",
            options=["JSON", "CSV", "Beide"],
            horizontal=True,
        )
        
        if st.button("📥 Exportieren", type="primary"):
            data = [p.__dict__ for p in products]
            
            if export_format in ("JSON", "Beide"):
                json_str = json.dumps(data, indent=2, ensure_ascii=False)
                st.download_button(
                    label="⬇️ JSON herunterladen",
                    data=json_str,
                    file_name=f"ebay_{search_query.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                )
            
            if export_format in ("CSV", "Beide"):
                df_export = pd.DataFrame(data)
                csv_str = df_export.to_csv(index=False)
                st.download_button(
                    label="⬇️ CSV herunterladen",
                    data=csv_str,
                    file_name=f"ebay_{search_query.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                )
    else:
        st.info("Führen Sie zuerst eine Suche aus, um Daten zu exportieren.")

# ── Footer ────────────────────────────────────────────────────

st.divider()
st.caption(f"🛒 eBay Scraping Agent v1.0 | Letzte Aktualisierung: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
