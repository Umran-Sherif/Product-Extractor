import tkinter as tk
import tkinter.messagebox as messagebox
from src.api import KeepaAPI
from src.product import Product
from datetime import datetime
import pandas as pd
from threading import Thread, Semaphore

## Displays token information from API for the user to determine how many requests they can excecute.

class TokenFrame(tk.LabelFrame):
    
    def __init__(self, parent, text):
        super().__init__(parent, text=text)

        self.api = KeepaAPI
        tokens = self.api.token_status()
        self.number_of_tokens = tk.Label(self, text=f'{tokens}', pady=5)

        self.frame_labels()
        self.refresh_button()

    # Display initial tokens
    def frame_labels(self):
        self.number_of_tokens.grid(row=0, column=0, padx=20)

    # Button to refresh token count
    def refresh_button(self):
        refresh = tk.Button(self, text="Refresh", command=TokenFrame.update_token_label)
        refresh.grid(row=0, column=1, padx=10)

    # Update display of taken label   
    def update_token_label(self):
        tokens = self.api.token_status()
        self.number_of_tokens.config(text=f'{tokens}')
                    

## Allows the user to check if the Brand is in Keepa's database, and how many products are available on each page of the brand.

class CheckInfoFrame(tk.LabelFrame):
    def __init__(self, parent, text, token_info_frame):
        super().__init__(parent, text=text)

        self.frame_labels()
        self.frame_inputs()
        self.brand_check_button()
        self.previous_brand = ""
        self.previous_page = ""
        self.ASINs = []
        self.api = KeepaAPI()
        self.token_info_frame = token_info_frame
        
        for widget in self.winfo_children():
            widget.grid_configure(padx=10, pady=3)

    # Displays labels in first row of frame
    def frame_labels(self):
        self.brand_name_label = tk.Label(self, text="Brand name")
        self.brand_name_label.grid(row=0, column=0)
        self.page_of_products_label = tk.Label(self, text="Page of products")
        self.page_of_products_label.grid(row=0, column=1)
        self.check_label = tk.Label(self, text="Cost: 10 tokens")
        self.check_label.grid(row=0, column=2)

    # Input fields for frame
    def frame_inputs(self):
        self.brand_name_entry = tk.Entry(self)
        self.brand_name_entry.grid(row=1, column=0)
        self.page_of_products_entry = tk.Spinbox(self, from_=1, to=10)
        self.page_of_products_entry.grid(row=1, column=1)
        
    # Produces a button for checking that the brand is available
    def brand_check_button(self):

        def check_brand():
            
            self.token_info_frame.update_token_label()
        
            brand = self.brand_name_entry.get()
            page = int(self.page_of_products_entry.get()) - 1
        
            if brand == "":
                messagebox.showinfo("Brand Check", "You must specify a brand")
        
            elif page == "":
                messagebox.showinfo("Brand Check", "You must specify a page number")
        
            else:
            
                if len(self.ASINs) == 0 or brand != self.previous_brand or page != self.previous_page:
                    filtered_products = self.api.get_filtered_products(brand, page)
                    self.ASINs = filtered_products['asinList']
                            
                    self.previous_brand = brand
                    self.previous_page = page
            
                number_of_asins = len(self.ASINs)
                messagebox.showinfo( "Brand Check", f"There are {number_of_asins} products on page {int(page) + 1} of the brand {brand}")
        
                self.token_info_frame.update_token_label()

        
        check = tk.Button(self, text="Check", command=check_brand)
        check.grid(row=1, column=2, pady=20)


## User can specify which product number they want to start from, and how many products they want to generate.

class OtherInfoFrame(tk.LabelFrame):
    def __init__(self, parent, text):
        super().__init__(parent, text=text)

        self.frame_labels()
        self.frame_inputs()

        for widget in self.winfo_children():
            widget.grid_configure(padx=10, pady=3)

    # Displays labels in first row of frame
    def frame_labels(self):
        self.starting_products_label = tk.Label(self, text="Start from product number:")
        self.starting_products_label.grid(row=2, column=0)
        self.how_many_products_label = tk.Label(self, text="How many products?")
        self.how_many_products_label.grid(row=2, column=1)
        self.how_many_products_info_label = tk.Label(self, text="Approx. 15 tokens per product")
        self.how_many_products_info_label.grid(row=4, column=1)

    # Input fields for frame
    def frame_inputs(self):
        self.starting_products_entry = tk.Spinbox(self, from_=1, to=50)
        self.starting_products_entry.grid(row=3, column=0)
        self.how_many_products_entry = tk.Spinbox(self, from_=1, to=20)
        self.how_many_products_entry.grid(row=3, column=1)

# Submit data to generate excel file.

class SubmitInfoFrame(tk.LabelFrame):
    def __init__(self, parent, text, token_info_frame, check_info_frame, other_info_frame):
        super().__init__(parent, text=text)

        self.api = KeepaAPI
        self.token_info_frame = token_info_frame
        self.check_info_frame = check_info_frame
        self.other_info_frame = other_info_frame
        self.list_of_products = []
        self.semaphore = Semaphore(20)  # Allow only x threads at a time
        self.submit_button()
        
        for widget in self.winfo_children():
            widget.grid_configure(padx=10, pady=3)

    # Button to refresh token count
    def submit_button(self):
        submit = tk.Button(self, text="Submit", command=self.generate_excel)
        submit.grid(row=0, column=1, padx=10)

    # Function to be called on concurrently on Thread
    def create_and_append_product_row(self, ASIN, i, thread_num):        
        try:
            with self.semaphore:
                product_row = Product.create_product_row(ASIN, i)
                self.list_of_products.append(product_row)
                print(f'Thread: {thread_num} - ASIN: {ASIN} created!\n')
        except Exception as e:
            print(f"Thread {thread_num} - ASIN: {i+1} failed! Here's the error: {str(e)}\nContinuing...")

    # Submit data to generate product file
    def generate_excel(self):
        self.brand = self.check_info_frame.brand_name_entry.get()
        self.page = int(self.check_info_frame.page_of_products_entry.get()) - 1
        start_from = int(self.other_info_frame.starting_products_entry.get()) - 1
        how_many = int(self.other_info_frame.how_many_products_entry.get())
    
        if self.brand == "" or self.page == "" or start_from == "" or how_many == "":
            messagebox.showinfo( "ASIN Filterer", f"Ensure you fill in all fields")
    
        else:
            filtered_products = self.api.get_filtered_products(self.brand, self.page)
            ASINs = filtered_products['asinList']
        
            self.token_info_frame.update_token_label()
            
            list_of_threads = []
            
            for i, ASIN in enumerate(ASINs[start_from:start_from+how_many]):
                thread_num = i + 1

                # Concurrently add rows to the product table
                thread = Thread(target=self.create_and_append_product_row, args=(ASIN, i, thread_num))
                
                # Start the thread
                thread.start()

                # store the thread object
                list_of_threads.append(thread)

            # Wait for all threads to complete
            for thread in list_of_threads:
                thread.join()

           # Schedule GUI update after threaded tasks are completed
            self.after(100, self.final_step)

    # Generation of file will execute here after threads complete
    def final_step(self):
        df = pd.DataFrame(self.list_of_products)
        print(df)
        
        now = datetime.now().strftime("%Y-%m-%d %H.%M.%S")
    
        filename = f'{self.brand} Product List, Page {int(self.page) + 1} - {now}.xlsx'
        df.to_excel(f'_Output//{filename}', index=False)
    
        messagebox.showinfo("ASIN Filterer", f'{filename} created!')

        self.token_info_frame.update_token_label()

        self.list_of_products = [] # reset list
