#!/usr/bin/env python
# coding: utf-8

# In[50]:


import requests
import sqlite3
import json
import re
import sys
import time

# Start the timer
start_time = time.time()


# In[52]:


username = 'U0000109430'
password = 'P$W1e6e18eda046d31af1bef867e1d944963'

filename = sys.argv[1]
db_name = filename + ".db"

# Connect to the SQLite database
conn = sqlite3.connect(db_name)

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Create a table to store URL and response
cursor.execute('''CREATE TABLE IF NOT EXISTS products
                  (url TEXT PRIMARY KEY, response TEXT)''')

# Store the URL and response in the table
def store_response(url, response):
    cursor.execute("INSERT INTO products (url, response) VALUES (?, ?)", (url, response))
    conn.commit()
    
def check_url_in_db(url_to_check):
    cursor.execute("SELECT COUNT(*) FROM products WHERE url = ?", (url_to_check,))
    count = cursor.fetchone()[0]
    return count


# In[ ]:


count = 0
with open(filename + ".txt", 'r') as file:
    for line in file:
        
        matches = re.findall(r'(https?://(?:www\.)?amazon\.[a-z]{2,6}\b(?:/[\w/:%#\$&\?\(\)~\.=\+\-]*)?)/ref=', line)
        for link in matches:
            task_params = {
                'target': 'amazon',
                'url': link,
                'parse': True,
            }

             
            if not check_url_in_db(link):
                print(link)
                response = requests.post(
                    'https://scrape.smartproxy.com/v1/tasks',
                    json = task_params,
                    auth = (username, password)
                )
                
                # Find the index of "dp/" in the URL
                dp_index = link.find("dp/") + 3

                # Extract the variant ID from the URL
                variant_id = link[dp_index:]


                # Check if the request was successful
                if response.status_code == 200:
                    # Get the JSON response
                    json_response = response.json()
                    json_data = json.dumps(json_response)
                    store_response(link, json_data)
                else:
                    # Handle the error response
                    print("API request failed with status code:", response.status_code)

conn.close()

end_time = time.time()
execution_time = end_time - start_time

# Print the execution time
print('Executed successfully')
print("Execution time: {:.2f} seconds".format(execution_time))
