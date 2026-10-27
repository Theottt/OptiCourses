import sys
import json
import re
from playwright.sync_api import sync_playwright

def parse_unit_price(unit_price_str):
    """Extrait la valeur numérique du prix au kilo/litre pour permettre le tri."""
    if not unit_price_str:
        return float('inf')
    
    match = re.search(r'([\d,\.]+)\s*€?\s*/\s*(kg|l|L|unité|pièce|Litre|KG)', unit_price_str, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1).replace(',', '.'))
        except ValueError:
            pass
            
    numbers = re.findall(r'[\d,\.]+', unit_price_str)
    if numbers:
        try:
            return float(numbers[0].replace(',', '.'))
        except ValueError:
            pass
            
    return float('inf')

def get_carrefour_products(query):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) # False pour voir le navigateur, True pour cacher
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        url = f"https://www.carrefour.fr/s?q={query}"
        print(f"Chargement de : {url}")
        
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # Ferme la bannière cookies si présente
        try:
            accept_button = page.locator("#onetrust-accept-btn-handler")
            if accept_button.is_visible(timeout=4000):
                accept_button.click()
                print("Cookies acceptés.")
        except:
            pass
        # Attend que les éléments produits soient visibles
        page.wait_for_timeout(4000)
    
        # Extraction ciblée incluant le prix unitaire
        print("Extraction des données...")
        products = page.evaluate("""() => {
            const items = [];
            // On cible les liens principaux de cartes produits
            const cards = document.querySelectorAll('a.product-card-click-wrapper');
            
            cards.forEach(card => {
                // Le titre est dans le texte du lien ou dans un span dédié
                const titleEl = card.querySelector('.product-card-title__text') || card;
                
                // On remonte au conteneur parent de la carte pour trouver le prix plus facilement
                const cardContainer = card.closest('article') || card.parentElement;
                
                let priceText = "Prix non trouvé";
                let unitPriceText = null;

                if (cardContainer) {
                    // Recherche d'éléments contenant le prix
                    const priceEl = cardContainer.querySelector('[class*="price"], .product-price__amount');
                    if (priceEl) {
                        priceText = priceEl.innerText.trim().replace(/\\n/g, ' ');
                    }
                    
                    // Recherche du prix unitaire (prix au kilo/litre)
                    const unitPriceEl = cardContainer.querySelector('.product-price__unit-price, [class*="unit-price"], [class*="prix-unitaire"]');
                    if (unitPriceEl) {
                        unitPriceText = unitPriceEl.innerText.trim().replace(/\\n/g, ' ');
                    }
                }

                if (titleEl) {
                    items.push({
                        titre: titleEl.innerText.trim(),
                        prix: priceText,
                        prix_unitaire: unitPriceText ? unitPriceText : "N/C",
                        lien: card.href
                    });
                }
            });
            return items;
        }""")

        browser.close()
        return products

if __name__ == "__main__":
    # Si l'utilisateur a passé un argument dans la ligne de commande (ex: python get_data.py pates)
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        # Sinon, message d'erreur propre pour éviter les blocages
        print("Erreur : Veuillez spécifier un produit à rechercher.")
        sys.exit(1)
        
    print(f"\nLancement de la recherche pour '{query}'...")
    results = get_carrefour_products(query)
    
    # Filtre anti-animaux si on cherche des pâtes
    if "pate" in query.lower():
        mots_interdits = ["chat", "chien", "croquette", "pâtée", "animal", "animaux", "litiere"]
        results = [prod for prod in results if not any(mot in prod['titre'].lower() for mot in mots_interdits)]
        
    # Calcul de la valeur numérique pour le tri par prix unitaire
    for prod in results:
        prod['valeur_unit'] = parse_unit_price(prod['prix_unitaire'])
        
    # Tri du moins cher au plus cher selon le prix unitaire
    results_sorted = sorted(results, key=lambda x: x['valeur_unit'])
    
    # Nettoyage de la clé temporaire de tri
    for prod in results_sorted:
        prod.pop('valeur_unit', None)
        
    # On ne garde que le Top 5
    top5 = results_sorted[:5]
        
    print(f"\nTOP 5 MEILLEURS PRIX/KG POUR '{query.upper()}' :\n" + "="*50)
    for i, prod in enumerate(top5, 1):
        print(f"{i}. {prod['titre']}")
        print(f"   Prix au kg/L : {prod['prix_unitaire']} (Prix paquet : {prod['prix']})")
        print(f"   Lien : {prod['lien']}\n")
    
    # Sauvegarde dans le JSON
    with open("carrefour_output.json", "w", encoding="utf-8") as f:
        json.dump(top5, f, indent=2, ensure_ascii=False)
    print("Les 5 meilleurs résultats ont été sauvegardés dans 'carrefour_output.json'.")