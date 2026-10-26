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

json_data = {
    'searchTerm': 'oeufs',
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

if response.status_code == 200:
    data = response.json()
    print("--- 🛒 LISTE DES PRODUITS TROUVÉS ---")
    
    # Le JSON de recherche de Carrefour renvoie souvent une liste de blocs
    for block in data:
        # On vérifie si le bloc contient des produits
        products = block.get('products', [])
        
        for prod in products:
            attrs = prod.get('attributes', {})
            title = attrs.get('title', 'Titre inconnu')
            brand = attrs.get('brand', 'Marque inconnue')
            
            # Récupération des offres de prix
            offers = attrs.get('offers', {})
            for ean, offer_data in offers.items():
                for store_id, offer_details in offer_data.items():
                    price_info = offer_details.get('attributes', {}).get('price', {})
                    price = price_info.get('price', 0.0)
                    per_unit = price_info.get('perUnitLabel', 'N/A')
                    
                    print(f"• {title} ({brand})")
                    print(f"  Prix : {price} € | Soit {per_unit}")
                    print("-" * 40)
else:
    print("Erreur lors de la récupération des données.")

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '{"searchTerm":"oeufs","categories":[],"productFilters":[{"key":"Platform","value":["Mobile"]}]}'
#response = requests.post('https://www.carrefour.fr/api/marketing/search', cookies=cookies, headers=headers, data=data)