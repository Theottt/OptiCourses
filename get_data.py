from playwright.sync_api import sync_playwright
import json

def get_carrefour_products(query="pates"):
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
    
        # Extraction ciblée basée sur ce qu'on vient de découvrir
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
                    // Recherche d'éléments contenant le prix (souvent dans des classes de type price)
                    const priceEl = cardContainer.querySelector('[class*="price"], .product-price__amount');
                    if (priceEl) {
                        priceText = priceEl.innerText.trim().replace(/\\n/g, ' ');
                    }
                }

                if (titleEl) {
                    items.push({
                        titre: titleEl.innerText.trim(),
                        prix: priceText,
                        lien: card.href
                    });
                }
            });
            return items;
        }""")

        browser.close()
        return products

if __name__ == "__main__":
    query = "pates"
    print(f"Lancement de la recherche pour '{query}'...")
    results = get_carrefour_products(query)
    
    print(f"\nSuccès ! {len(results)} produits extraits.")
    
    # Affichage des 5 premiers résultats dans la console
    for i, prod in enumerate(results[:5], 1):
        print(f"\n{i}. Titre : {prod['titre']}")
        print(f"   Prix  : {prod['prix']}")
        print(f"   Lien  : {prod['lien']}")
    
    # Sauvegarde dans un fichier JSON pour OptiCourses
    with open("carrefour_output.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("\nLes données ont été sauvegardées dans 'carrefour_output.json'.")