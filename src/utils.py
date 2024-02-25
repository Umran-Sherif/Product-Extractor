# Util class with helper functions for package.

import time as t
from datetime import datetime

# Present an integer price into a legible string.
    
def price_string(product_price):
    return f'£{product_price/100:.2f}'

# Create a google search url from a search term, using a product name / product ID.

def create_google_search_url(product_name_or_identifier):
    base_url = "https://www.google.com/search?q="
    query = product_name_or_identifier.replace(" ", "%20").replace(",", '')
    google_search_url = base_url + query
    return google_search_url

# Create a trolley search url from a search term, using a product name.

def create_trolley_search_url(product_name):
    base_url = "https://www.trolley.co.uk/search/?from=search&q="
    query = product_name.replace(" ", "+")
    trolley_search_url = base_url + query
    return trolley_search_url

# Create an excel hyperlink cell for a url.

def make_hyperlink(suffix):
    return '=HYPERLINK("%s")' % (suffix)

 # Convert timestamps given by Keepa API to datetime (keepa min)
    
def unix_epoch_time_to_dt(timestamp):
    dt = datetime.fromtimestamp(((timestamp + 21564000) * 60000)/1000)
    return [dt.strftime("%Y-%m-%d - %H:%M:%S"), dt]

 # Convert epoch to datetime

def epoch_to_dt(timestamp):
    dt = datetime.fromtimestamp( timestamp/1000 )
    return dt.strftime("%Y-%m-%d - %H:%M:%S")


## Decorators

# Can be used as a decorator for any function to determine how long it takes to run.

def time_taken(func):
    def wrapper(*args, **kwargs):
        t1 = t.time()
        result = func(*args, **kwargs)
        t2 = t.time()
        print(f"Time taken to execute {func.__name__}: {(t2-t1):.1f} secs")
        return result
    return wrapper

