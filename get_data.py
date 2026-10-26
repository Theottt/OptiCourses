import os
from dotenv import load_dotenv
from curl_cffi import requests

# 1. Charger les variables d'environnement depuis le fichier .env
load_dotenv()

COOKIE_STR = os.getenv("CARREFOUR_COOKIE")
USER_AGENT_STR = os.getenv("CARREFOUR_USER_AGENT")

# 2. Préparer les en-têtes et le corps de la requête
headers = {
    'accept': '*/*',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/json',
    'origin': 'https://www.carrefour.fr',
    'referer': 'https://www.carrefour.fr/s?q=oeufs',
    'user-agent': USER_AGENT_STR,
    'cookie': COOKIE_STR,
    'x-requested-with': 'XMLHttpRequest',
}

produit_cherche = input("Quel produit veux-tu chercher ? ")

json_data = {
    'searchTerm': produit_cherche,
    'categories': [],
    'productFilters': [
        {
            'key': 'Platform',
            'value': ['Mobile'],
        },
    ],
}

# 3. Envoi de la requête sécurisée
response = requests.post(
    'https://www.carrefour.fr/api/marketing/search',
    headers=headers,
    json=json_data,
    impersonate="chrome"
)

produits_analyses = []

if response.status_code == 200:
    data = response.json()
    
    for block in data:
        products = block.get('products', [])
        for prod in products:
            attrs = prod.get('attributes', {})
            title = attrs.get('title', 'Titre inconnu')
            brand = attrs.get('brand', 'Marque inconnue')
            
            offers = attrs.get('offers', {})
            for ean, offer_data in offers.items():
                for store_id, offer_details in offer_data.items():
                    price_info = offer_details.get('attributes', {}).get('price', {})
                    price = price_info.get('price', 0.0)
                    per_unit_str = price_info.get('perUnitLabel', '')
                    
                    per_unit_price = 0.0
                    try:
                        # Nettoie la chaîne pour garder juste le nombre (ex: "5.83")
                        clean_str = per_unit_str.split('€')[0].strip().replace(',', '.')
                        per_unit_price = float(clean_str)
                    except:
                        pass
                    
                    # On stocke dans une liste propre
                    produits_analyses.append({
                        "title": title,
                        "brand": brand,
                        "price": price,
                        "per_unit_price": per_unit_price,
                        "per_unit_label": per_unit_str
                    })

    # --- 2. LE TRI AUTOMATIQUE (Du moins cher au plus cher au kilo) ---
    # On trie la liste en fonction du prix unitaire (en s'assurant qu'il est supérieur à 0)
    produits_tries = sorted([p for p in produits_analyses if p["per_unit_price"] > 0], key=lambda x: x["per_unit_price"])

    print(f"\n--- TOP DES MEILLEURES AFFAIRES (TRIÉES PAR PRIX AU KILO) ---")
    for i, p in enumerate(produits_tries[:3], 1): # Affiche le Top 3
        print(f"{i}. {p['title']}")
        print(f"   Prix total : {p['price']} € | ➔ {p['per_unit_label']}")
        print("-" * 40)

else:
    print("Erreur lors de la récupération des données.")

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '{"searchTerm":"oeufs","categories":[],"productFilters":[{"key":"Platform","value":["Mobile"]}]}'
#response = requests.post('https://www.carrefour.fr/api/marketing/search', cookies=cookies, headers=headers, data=data)