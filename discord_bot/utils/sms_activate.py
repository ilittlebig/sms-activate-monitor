#
#
# Author: Elias Sjödin
# Created: 2025-01-29

import requests

def check_gmx_stock(sms_api_key, country_id=None):
    url = "https://api.sms-activate.org/stubs/handler_api.php"
    params = {
        "api_key": sms_api_key,
        "action": "getNumbersStatus",
        "country": country_id if country_id else 0
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        gmx_stock = data.get("abk", 0)
        return int(gmx_stock)
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch GMX stock: {e}")
    except KeyError:
        raise Exception("GMX stock data is unavailable in the API response.")
