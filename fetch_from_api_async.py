import asyncio
import aiohttp
import sqlite3
import json
import re
import sys
import time

# Start the timer
start_time = time.time()

# ...
count = 1

async def process_url(session, url):
    global count
    
    count+=1
    task_params = {
        'target': 'amazon',
        'url': url,
        'parse': True,
    }

    # task_params = {
    #     'count': count,
    #     'url': url,
    #     'parse': True,
    # }

    if not check_url_in_db(url):
        print(url)
        async with session.post(
            'https://scrape.smartproxy.com/v1/tasks',
            json=task_params,
            auth=aiohttp.BasicAuth(username, password)
        ) as response:
            

            if response.status == 200:
                json_response = await response.json()
                json_data = json.dumps(json_response)
                
                store_response(url, json_data)
            else:
                print("API request failed with status code:", response.status)

def store_response(url, response):
    cursor.execute("INSERT INTO products (url, response) VALUES (?, ?)", (url, response))
    conn.commit()

def check_url_in_db(url_to_check):
    cursor.execute("SELECT COUNT(*) FROM products WHERE url = ?", (url_to_check,))
    count = cursor.fetchone()[0]
    return count

async def process_file(filename):
    async with aiohttp.ClientSession() as session:
        with open(filename + ".txt", 'r') as file:
            lines = file.readlines()

        tasks = []
        for line in lines:
            matches = re.findall(r'(https?://(?:www\.)?amazon\.[a-z]{2,6}\b(?:/[\w/:%#\$&\?\(\)~\.=\+\-]*)?)/ref=', line)
            for link in matches:
                task = asyncio.create_task(process_url(session, link))
                tasks.append(task)

        await asyncio.gather(*tasks)

# ...

if __name__ == '__main__':
    username = 'U0000109430'
    password = 'P$W1e6e18eda046d31af1bef867e1d944963'

    filename = sys.argv[1]
    db_name = filename + ".db"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS products
                      (url TEXT PRIMARY KEY, response TEXT)''')

    print("Processing file:", filename)
    asyncio.run(process_file(filename))

    conn.close()

    end_time = time.time()
    execution_time = end_time - start_time

    # Print the execution time
    print('Executed successfully')
    print("Execution time: {:.2f} seconds".format(execution_time))
    
