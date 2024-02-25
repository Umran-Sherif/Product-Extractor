from .utils import create_google_search_url, create_trolley_search_url, make_hyperlink, price_string, unix_epoch_time_to_dt, time_taken
from datetime import datetime
from .api import KeepaAPI as api

class Product():

    @classmethod
    def create_product_row(cls, ASIN, i):
        product_data = api.get_product_data(ASIN)

        TARGET_ROI = 0.25
        product = product_data['products'][0]
        
        ## One-liner calculations
        
        price = product['csv'][18][-2]
        timestamp = product['csv'][18][-3]
        asin = product['asin']
        product_name = product['title']
        brand = product['brand']
        main_category = product['categoryTree'][0]['name']
        default_sell_price = price
        buybox_price = price
        profit = f'=IF(E{i+2}=0, CONCATENATE("£",H{i+2}-AB{i+2}-F{i+2}), CONCATENATE("£",H{i+2}-AB{i+2}-E{i+2}))'
        roi = f'=IFERROR(IF(E{i+2}=0, CONCATENATE(ROUND((J{i+2}/F{i+2})*100,1), "%"), CONCATENATE(ROUND((J{i+2}/E{i+2})*100,1), "%")),"")'
        breakeven_price = f'=E{i+2}+AB{i+2}'
        length = product['packageLength']
        height = product['packageHeight']
        width = product['packageWidth']
        weight = product['packageWeight']
        quantity = product['packageQuantity']
        current_date = datetime.now().strftime('%Y-%m-%d')
        bought_last_month = "" if 'monthlySold' not in product else product['monthlySold']
        
        
        ## Multi-liner calculations
        
        # URLs
        limited_chars_product_name = ' '.join(product_name.split(" ")[:15])
        google_search_url = create_google_search_url(limited_chars_product_name)
        trolley_search_url = create_trolley_search_url(limited_chars_product_name)
        amz_url = "https://www.amazon.co.uk/dp/" + asin
        
        # BSR calculation
        main_category_id = str(product['categoryTree'][0]['catId'])
        main_bsr_list = [""] if main_category_id not in product["salesRanks"] else product["salesRanks"][main_category_id]
        bsr =  main_bsr_list[-1]
        
        # Fees
        
        fba_fee = 0 if product['fbaFees'] == None else product['fbaFees']['pickAndPackFee']
        referral_fee_percent = 0 if 'referralFeePercent' not in product else product['referralFeePercent']
        referral_fee = (referral_fee_percent/100) * float(price)
        storage_fee = (
            length * height * width 
            ) / (2.832 * 10000000) * 0.78 * 100
        vat_fee = (0.2 * (fba_fee + referral_fee + storage_fee))
        total_fee = fba_fee + referral_fee + storage_fee + vat_fee
        
        # Special prices
        
        if total_fee == 0:
            BB_roi_buy_price = 0
            BB_margin_buy_price = 0
        else:
            BB_roi_buy_price = (buybox_price - total_fee) / (1 + TARGET_ROI)    # Maximum buy cost to hit ROI percentage
        
            amount_over_a_pound = (buybox_price-BB_roi_buy_price-total_fee-100)
            
            if amount_over_a_pound > 0:
                BB_margin_buy_price = price_string(BB_roi_buy_price + amount_over_a_pound)
            else:
                BB_margin_buy_price = ""
        
        # Amazon & Third-party Sellers
        
        offers = product['offers']
        number_of_sellers = 0
        number_of_fbas = 0
        number_of_fbms = 0
        amzn_on_listing = "No"
        
        for offer in offers:
            last_seen = unix_epoch_time_to_dt(offer['lastSeen'])
            
            if last_seen[1].strftime("%Y-%m-%d") == datetime.now().strftime("%Y-%m-%d") or last_seen[1].strftime("%Y-%m-%d") == (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"):
                
                number_of_sellers += 1
        
                if offer['isAmazon'] == True:
                    amzn_on_listing = "Yes"
        
                if offer['isFBA'] == True:
                    number_of_fbas += 1
        
                if offer['isShippable'] == True and offer['isFBA'] == False and offer['isAmazon'] == False:
                    number_of_fbms += 1
        
        # Maximum historical buybox price
        
        buybox_history_tuple = product['csv'][18]
        price_history = []
        
        for i in range(1, len(buybox_history_tuple), 3):
            price_history.append(buybox_history_tuple[i])
        
        max_buybox_price = max(price_history)
        
        # Date product was released
        
        rd = str(product['releaseDate'])
        date_released = f'{rd[:4]}-{rd[4:6]}-{rd[6:]}'
        tracked_since = unix_epoch_time_to_dt(product['trackingSince'])[0]
        
        
        
        ## Collect all variables into a dictionary, representing rows in the final generated output.
        
        product_row = {
            'ASIN': asin, 
            'Product Name': product_name,
            'Brand': brand, 
            'Category': main_category, 
            'Buy Price': '',                  # enter in sheet manually
            '25% ROI': price_string(BB_roi_buy_price),      # based on buybox price
            'BB Margin Buy Price': BB_margin_buy_price,
            'Sell Price': price_string(default_sell_price),
            'Buybox Price' : price_string(buybox_price), 
            'Profit': profit,                     # based on buy price, formula in sheet
            'ROI': roi,                        # based on buy price, formula in sheet
            'Amz URL': make_hyperlink(amz_url), 
            'Google Search': make_hyperlink(google_search_url),
            'Trolley Search': make_hyperlink(trolley_search_url),
            'Source URL': ' ',                 # enter in sheet manually
            'Notes': ' ',                      # enter in sheet manually 
            'Date': current_date, 
            'BSR': bsr, 
            'Bought last month': bought_last_month,
            'Amazon?': amzn_on_listing,
            'FBA sellers': number_of_fbas,
            'FBM sellers': number_of_fbms,
            'No. sellers': number_of_sellers,
            'B/E Sell Price': breakeven_price,                # based on buy price, formula in sheet
            'SP Max Buy Price': '',              # based on sell price, formula in sheet
            'BP Max Sold Price': '',             # based on buy price, formula in sheet
            'Max Buybox Price': price_string(max_buybox_price),
            'Total Fees': price_string(total_fee),
            'FBA Fee': price_string(fba_fee), 
            'Referral Fee': price_string(referral_fee), 
            'Storage_fee': price_string(storage_fee), 
            'VAT fee': price_string(vat_fee),
            'Dimensions (cm)': f"L:{length/100} x H:{height/100} x W:{width/100}",
            'Weight (kg)': weight/1000,
            'Quantity': quantity,
            'Date Released': date_released,
            'Keepa Data Since': tracked_since,
        }
        
        return product_row