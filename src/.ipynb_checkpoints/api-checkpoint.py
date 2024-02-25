import requests
import json
import urllib.parse as ubp
from .utils import time_taken, epoch_to_dt

class KeepaAPI():
    BASE_URL = "https://api.keepa.com/"
    
    with open("_data//credentials.json", 'r') as file:
        API_KEY = json.load(file)['KEEPA_API_KEY']
        TOKEN_URL = f'{BASE_URL}token?key={API_KEY}'

    # Checking currently available tokens

    @staticmethod
    def token_status():
        response = requests.get(KeepaAPI.TOKEN_URL)

        print(f"API Request status: {response}")
        
        data = response.json()
        
        data['timestamp'] = epoch_to_dt(data['timestamp'])
        
        return f"Tokens Left: {data['tokensLeft']}"

    # Decorator for displaying token count after a function is called

    @staticmethod
    def token_count(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            print(KeepaAPI.token_status())
            return result
        return wrapper

    # Generate products within a brand meeting conditions
    
    @classmethod
    @token_count
    @time_taken
    def get_filtered_products(cls, brand, page, min_price=4, max_price=50, min_sales_rank=99, max_sales_rank=120000):
        base_url = f'{cls.BASE_URL}query?key={cls.API_KEY}&domain=2&selection='
    
        # Convert Keepa category ID (integer) to a list of integers as required by the API
        # categories = [category]
    
        params = {
            "brand": brand,
            "current_SALES_gte": min_sales_rank,   # Lowest BSR
            "current_SALES_lte": max_sales_rank,           # Highest BSR limit
            "current_BUY_BOX_SHIPPING_gte": min_price*100,
            "current_BUY_BOX_SHIPPING_lte": max_price*100,
            "sort": [["current_SALES","asc"]],
            "productType": [0,1],
            "page": page,
            "perPage": 50,
        }
        
        if params != "":
            encoded_params = ubp.quote(json.dumps(params))
            url = f"{base_url}{encoded_params}"
            
        else:
            url = f"{base_url}"
        
        response = requests.get(url)
    
        if response.status_code == 200:
            return response.json()
        else:
            print("Error: Unable to fetch products.")
            print(response)
            return None

    # Generate product data for an ASIN

    @classmethod
    @token_count
    @time_taken
    def get_product_data(cls, asin):
    
        details = {}
                
        url = f"{cls.BASE_URL}product?key={cls.API_KEY}&domain=2&asin={asin}&offers=20&only-live-offers=1"
        response = requests.get(url)
        data = response.json()
            
        return data