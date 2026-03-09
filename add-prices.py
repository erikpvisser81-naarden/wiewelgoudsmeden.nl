#!/usr/bin/env python3
"""Add prices to Wiewel Goudsmeden product pages and collectie overview."""
import os, re

BASE = r"c:\Users\Gebruiker\OneDrive\Bureaublad\wiewelgoudsmeden.nl"

# Complete price database scraped from live WordPress site (9 maart 2026)
# slug -> (price_euros, price_display, category)
# None = "Op aanvraag"
PRICES = {
    # RINGEN
    "alliance-roze-spinellen": (9350, "€ 9.350", "ringen"),
    "cacholong-opaal-aquamarijn-ring": (8865, "€ 8.865", "ringen"),
    "gele-diamant-ring": (6095, "€ 6.095", "ringen"),
    "maansteen-saffieren-ring": (3335, "€ 3.335", "ringen"),
    "platina-ring-groene-saffier": (10327, "€ 10.327", "ringen"),
    "ring-rutielkwarts-diamant": (5700, "€ 5.700", "ringen"),
    "witgouden-alliance-diamant": (12000, "€ 12.000", "ringen"),
    "alliance-briljant-diamant": (10285, "€ 10.285", "ringen"),
    "alliance-platina-asscher": (29150, "€ 29.150", "ringen"),
    "platina-alliance-princess": (11980, "€ 11.980", "ringen"),
    "geelgouden-aanschuifring": (1045, "€ 1.045", "ringen"),
    "ring-zuidzeeparel-groene-diamant": (1915, "€ 1.915", "ringen"),
    "ring-tahiti-parel": (2915, "€ 2.915", "ringen"),
    "ring-zuidzeeparel": (2245, "€ 2.245", "ringen"),
    "peridot-diamanten-ring": (3905, "€ 3.905", "ringen"),
    "platina-ring-blauwe-saffier": (10890, "€ 10.890", "ringen"),
    "platina-ring-bruine-diamant": (2965, "€ 2.965", "ringen"),
    "ring-groene-toermalijn": (10050, "€ 10.050", "ringen"),
    "ring-paarse-jade": (15160, "€ 15.160", "ringen"),
    "ring-rubeliet-diamant": (7895, "€ 7.895", "ringen"),
    "ring-turkoois": (3675, "€ 3.675", "ringen"),
    "ring-toermalijnkwarts": (4610, "€ 4.610", "ringen"),
    "ring-mandarijngranaat": (5165, "€ 5.165", "ringen"),
    # Sandy rings - not in our local pages
    # Witgouden ring rode/witte diamant - not in our local pages
    # Witgouden diamanten solitair - not in our local pages
    # Zilver en gouden ring granaat - not in our local pages
    # Zilveren ring Paraiba - not in our local pages
    # Zilveren ring roze toermalijn - not in our local pages

    # OORBELLEN
    "bruine-diamant-koraal-oorbellen": (3395, "€ 3.395", "oorbellen"),
    "creolen-amethist-trosjes": (3580, "€ 3.580", "oorbellen"),
    "creolen-spinel-trosjes": (6075, "€ 6.075", "oorbellen"),
    "creolen-tanzaniet-trosjes": (5655, "€ 5.655", "oorbellen"),
    "diamant-zoetwaterparel-oorhaken": (1780, "€ 1.780", "oorbellen"),
    "diamanten-tweezijdige-creolen": (11500, "€ 11.500", "oorbellen"),
    "gouden-zuidzee-pareloorbellen": (1460, "€ 1.460", "oorbellen"),
    "oorclips-amethist-zoetwaterparel": (3950, "€ 3.950", "oorbellen"),
    "oorhaken-amethist": (1090, "€ 1.090", "oorbellen"),
    "oorhaken-turkoois": (2945, "€ 2.945", "oorbellen"),
    "oorhangers-witte-zoetwaterparel": (980, "€ 980", "oorbellen"),
    "roze-maansteen-diamanten-oorhaken": (2700, "€ 2.700", "oorbellen"),
    "solitair-oorstekers-triangel-diamant": (2270, "€ 2.270", "oorbellen"),
    "witgouden-agaat-oorhaken": (1285, "€ 1.285", "oorbellen"),
    "witgouden-creolen": (3820, "€ 3.820", "oorbellen"),
    "witgouden-creolen-diamant": (5390, "€ 5.390", "oorbellen"),
    "zuidzeeparel-citrien-pampels": (2315, "€ 2.315", "oorbellen"),
    "geelgouden-creolen": (None, "Op aanvraag", "oorbellen"),
    "geelgouden-gladde-creolen": (1990, "€ 1.990", "oorbellen"),
    "grote-barnsteen-oorbellen": (1030, "€ 1.030", "oorbellen"),
    "mammoet-ivoor-oorbellen": (1030, "€ 1.030", "oorbellen"),
    "maud-geelgouden-creolen": (1815, "€ 1.815", "oorbellen"),
    "maud-diamanten-creolen": (None, "Op aanvraag", "oorbellen"),
    "gestreepte-agaat-oorbellen": (910, "€ 910", "oorbellen"),
    "lemon-chrysopraas-oorbellen": (910, "€ 910", "oorbellen"),
    "oorbellen-maansteen-blauwe-saffier": (1390, "€ 1.390", "oorbellen"),
    "oorbellen-maansteen-chalcedoon": (4660, "€ 4.660", "oorbellen"),
    "oorbellen-toermalijnkwarts": (575, "€ 575", "oorbellen"),
    "oorclips-mammoet-ivoor-hout": (5995, "€ 5.995", "oorbellen"),
    "solitair-oorstekers-diamant": (5650, "€ 5.650", "oorbellen"),
    "robijn-oorstekers": (3630, "€ 3.630", "oorbellen"),
    "tahiti-parel-oorbellen": (4175, "€ 4.175", "oorbellen"),
    "tweekleurige-tahitiparel-oorbellen": (1280, "€ 1.280", "oorbellen"),

    # COLLIERS
    "collier-indigoliet-toermalijn": (6595, "€ 6.595", "colliers"),
    "fijn-gele-saffier-collier": (990, "€ 990", "colliers"),
    "fijn-multicolour-bruin-saffier-collier": (940, "€ 940", "colliers"),
    "fijn-multicolour-saffier-collier": (875, "€ 875", "colliers"),
    "fijn-multicolour-toermalijn-collier": (820, "€ 820", "colliers"),
    "rubeliet-collier": (940, "€ 940", "colliers"),
    "fijn-toermalijnsnoer-blauw": (855, "€ 855", "colliers"),
    "groen-barnsteen-collier": (2270, "€ 2.270", "colliers"),
    "lang-bloedkoraal-collier": (2200, "€ 2.200", "colliers"),
    "multicolour-koraal-collier": (2250, "€ 2.250", "colliers"),
    "roze-spinel-collier": (1850, "€ 1.850", "colliers"),
    "snoer-zwarte-spinel": (330, "€ 330", "colliers"),
    "platina-collier-bruine-diamant": (4810, "€ 4.810", "colliers"),
    "mammoet-ebbenhout-collier": (5570, "€ 5.570", "colliers"),
    "mammoet-collier": (4235, "€ 4.235", "colliers"),
    "roze-zoetwater-parelsnoer": (1060, "€ 1.060", "colliers"),
    "barok-tahiti-parel-collier": (2240, "€ 2.240", "colliers"),
    "tahiti-parelsnoer-luxe-sluiting": (None, "Op aanvraag", "colliers"),
    "zoetwater-parelsnoer": (3450, "€ 3.450", "colliers"),
    "collier-ruwe-spinel": (720, "€ 720", "colliers"),
    "zilveren-hanger-eikeltje": (935, "€ 935", "colliers"),

    # ARMBANDEN
    "armband-hexagon-zwarte-diamant": (2980, "€ 2.980", "armbanden"),
    "armband-zeshoek-sluiting": (4500, "€ 4.500", "armbanden"),
    "minimalistische-cuff-armband": (None, "Op aanvraag", "armbanden"),
    "geelgouden-schakelarmband": (None, "Op aanvraag", "armbanden"),
    "geelgouden-slavenarmband": (None, "Op aanvraag", "armbanden"),

    # MANCHETKNOPEN
    "primavera-manchetknopen-geelgoud": (3470, "€ 3.470", "manchetknopen"),
    "primavera-manchetknopen-witgoud": (5670, "€ 5.670", "manchetknopen"),
    "maansteen-manchetknopen": (5060, "€ 5.060", "manchetknopen"),
    "octopus-manchetknopen": (8570, "€ 8.570", "manchetknopen"),
    "parelmoer-manchetknopen": (3110, "€ 3.110", "manchetknopen"),
    "zeshoek-manchetknopen": (3680, "€ 3.680", "manchetknopen"),

    # BROCHES
    "dasspeld-makelaarsstaf": (335, "€ 335", "broches"),
    "saffier-broche": (None, "Op aanvraag", "broches"),
    "vlieg-speldje": (515, "€ 515", "broches"),
}

PHONE_CTA_HTML = """
            <!-- High-value phone CTA -->
            <div class="pdp__phone-cta">
              <p class="pdp__phone-label">Interesse in dit sieraad?</p>
              <a href="tel:+31850668950" class="pdp__phone-btn">
                <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M6.62 10.79a15.05 15.05 0 006.59 6.59l2.2-2.2a1 1 0 011.01-.24 11.36 11.36 0 003.58.57 1 1 0 011 1v3.49a1 1 0 01-1 1A17 17 0 013 5a1 1 0 011-1h3.5a1 1 0 011 1 11.36 11.36 0 00.57 3.58 1 1 0 01-.25 1.01l-2.2 2.2z" fill="currentColor"/></svg>
                Bel ons: 085-066 8950
              </a>
              <p class="pdp__phone-note">Wij adviseren u graag persoonlijk</p>
            </div>
"""

def update_product_page(slug):
    """Add price + phone CTA to a product detail page."""
    filepath = os.path.join(BASE, "collectie", f"{slug}.html")
    if not os.path.exists(filepath):
        print(f"  SKIP (file not found): {slug}")
        return False

    if slug not in PRICES:
        print(f"  SKIP (no price data): {slug}")
        return False

    price_val, price_display, category = PRICES[slug]

    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    # Skip if already has price
    if "pdp__price" in html:
        print(f"  SKIP (already has price): {slug}")
        return False

    modified = False

    # 1. Add price display after pdp__subtitle
    if price_val is not None:
        price_html = f'            <p class="pdp__price">{price_display}</p>'
    else:
        price_html = '            <p class="pdp__price pdp__price--request">Prijs op aanvraag</p>'

    # Insert after the subtitle line
    subtitle_pattern = r'(<p class="pdp__subtitle">.*?</p>)'
    if re.search(subtitle_pattern, html):
        html = re.sub(subtitle_pattern, r'\1\n' + price_html, html, count=1)
        modified = True

    # 2. Add price to JSON-LD Product schema
    if price_val is not None:
        # Add price + currency to the Offer
        old_offer = '"availability": "https://schema.org/InStock"'
        new_offer = f'"price": "{price_val}.00",\n      "priceCurrency": "EUR",\n      "availability": "https://schema.org/InStock"'
        if old_offer in html:
            html = html.replace(old_offer, new_offer, 1)
            modified = True

    # 3. Add phone CTA for products >= 5000
    if price_val is not None and price_val >= 5000:
        # Insert before the regular CTA block
        cta_marker = '            <!-- CTA -->'
        if cta_marker in html and "pdp__phone-cta" not in html:
            html = html.replace(cta_marker, PHONE_CTA_HTML + "\n" + cta_marker, 1)
            modified = True

    if modified:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        label = "HIGH VALUE" if (price_val and price_val >= 5000) else ""
        print(f"  OK: {slug} -> {price_display} {label}")
        return True
    return False


def update_collectie_overview():
    """Add prices to the product cards on collectie.html."""
    filepath = os.path.join(BASE, "collectie.html")
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    if "product-card__price" in html:
        print("  collectie.html already has prices, skipping")
        return

    # For each product card, find the href slug and insert price after material line
    def add_price_to_card(match):
        card_html = match.group(0)
        # Extract slug from href
        href_match = re.search(r'href="collectie/([^"]+)\.html"', card_html)
        if not href_match:
            return card_html
        slug = href_match.group(1)
        if slug not in PRICES:
            return card_html

        price_val, price_display, _ = PRICES[slug]
        if price_val is not None:
            price_line = f'                <span class="product-card__price">{price_display}</span>'
        else:
            price_line = '                <span class="product-card__price product-card__price--request">Prijs op aanvraag</span>'

        # Insert after the material line (product-card__material)
        card_html = re.sub(
            r'(<p class="product-card__material">.*?</p>)',
            r'\1\n' + price_line,
            card_html, count=1
        )
        return card_html

    # Match each product card article
    html = re.sub(
        r'<article class="product-card">.*?</article>',
        add_price_to_card,
        html,
        flags=re.DOTALL
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    print("  OK: collectie.html updated with prices")


if __name__ == "__main__":
    print("=== Updating product detail pages ===")
    updated = 0
    skipped = 0
    for slug in sorted(PRICES.keys()):
        if update_product_page(slug):
            updated += 1
        else:
            skipped += 1
    print(f"\nProduct pages: {updated} updated, {skipped} skipped")

    print("\n=== Updating collectie overview ===")
    update_collectie_overview()

    print("\nDone!")
