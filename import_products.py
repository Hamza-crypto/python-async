#!/usr/bin/env python
# coding: utf-8

# In[1]:


from woocommerce import API
import sqlite3
import json
import re
import sys


# In[14]:


with open('config.json', 'r') as file:
    config_data = json.load(file)
    
wcapi = API(
    url=config_data['url'],
    consumer_key=config_data['consumer_key'],
    consumer_secret=config_data['consumer_secret'],
    version=config_data['version'],
    timeout=60
)    


# In[40]:
category_id = sys.argv[2]
filename = sys.argv[1]
db_name = filename + ".db"

conn = sqlite3.connect(db_name)

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Execute a SELECT statement to retrieve data from a table
cursor.execute('SELECT * FROM products')

# Fetch all the rows returned by the SELECT statement
rows = cursor.fetchall()




# In[39]:


def convert_image_array(images):
    converted_images = []
    for image_url in images:
        converted_images.append({"src": image_url})
    return converted_images



for row in rows:
    print(row[0])
    try:
        json_data = row[1]  # Assuming the JSON data is stored in the first column of the row
        parsed_data = json.loads(json_data)
        #categories = parsed_data['results'][0]['content']['category'][0]['ladder']
        #category_ids = create_category( categories, existing_categories)

        # Access specific information from the JSON data
        product_title = parsed_data['results'][0]['content']['title']
        print(product_title)
        product_price = parsed_data['results'][0]['content']['price']
        product_sku = parsed_data['results'][0]['content']['asin']
        product_description = parsed_data['results'][0]['content']['description']
        product_short_description = parsed_data['results'][0]['content']['bullet_points']
        product_images = parsed_data['results'][0]['content']['images']

        product_images = convert_image_array(product_images)

        data = {
        "name": product_title,
        "type": "simple",
        "regular_price": str(product_price),
        "sku": product_sku,
        "description": product_description + "\n\n\n" + product_short_description,
        "categories": [
                        {"id": category_id}
                      ],
        "images": product_images
        }

        
        print('Downloading images ...')
        product_response = wcapi.post("products", data).json()
        if "id" in product_response:
            print(f"Product ID:  '{product_response['id']}'")
        else:    
            print(product_response)

    except Exception as e:
        print("something went wrong")
        print(e)
    print('---------------------------------------------------------------------------')    
    #break    

print('Products Imported successfully')
conn.close()