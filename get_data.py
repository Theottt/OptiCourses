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

print("Code de retour HTTP :", response.status_code)
if response.status_code == 200:
    print("Succès ! Données reçues :")
    print(response.json())

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '{"searchTerm":"oeufs","categories":[],"productFilters":[{"key":"Platform","value":["Mobile"]}]}'
#response = requests.post('https://www.carrefour.fr/api/marketing/search', cookies=cookies, headers=headers, data=data)