import requests
import os
import pandas as pd 
import json
import time

#List of US States
state_names = ["Alaska", "Alabama", "Arkansas", "Arizona", 
               "California", "Colorado", "Connecticut", 
               "Delaware", "Florida", "Georgia", "Hawaii", 
               "Iowa", "Idaho", "Illinois", "Indiana", 
               "Kansas", "Kentucky", "Louisiana", "Massachusetts", 
               "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", 
               "Mississippi", "Montana", "North Carolina", "North Dakota", 
               "Nebraska", "New Hampshire", "New Jersey", "New Mexico", 
               "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", 
               "Rhode Island", "South Carolina", "South Dakota", "Tennessee", 
               "Texas", "Utah", "Virginia", "Vermont", "Washington", 
               "Wisconsin", "West Virginia", "Wyoming"]

#Sort & Uppercase everything
state_names = sorted([s.upper() for s in state_names])

#API Call function for each state & paginated response
def get_paginated_responses(state, i):
    #get the api key needed to request data
    api_key = os.environ['API_KEY']
    #Make state folders as you iterate in current working directory
    out_folder = 'DATA'
    state_path = os.path.join(out_folder, state)
    if not os.path.exists(state_path):
        os.mkdir(state_path)
    #query filters
    source = r'source:("The New York Times")'
    state_query = f'glocations:("{state}")'
    #file name. i = the paginated. There will be 10 total responses in each paginated response
    file = f'{state}_page_{i}.json'
    #define the output
    out_path = os.path.join(state_path, file)
    #Search articles about each state written by The New York Times since 2000
    request_url = f'https://api.nytimes.com/svc/search/v2/articlesearch.json?fq={state_query} AND {source}\
        &begin_date=20000101&page={i}&api-key={api_key}'
    r = requests.get(request_url)
    api_response = json.loads(r.content)
    #save the json file
    with open(out_path, 'w') as f:
        json.dump(api_response, f)


#Get 10 paginated responses per state

#Each response should have 10 articles - resulting in 100 articles per state
ranges = [(i, i + 4) for i in range(0, 10) if i % 5 == 0]

#Per the docs you can only make 5 calls per minute
for state in state_names:
    for r in ranges:
        pages = [i for i in range(r[0], r[1] + 1)]
        for page in pages:
            get_paginated_responses(state, page)
        #wait a 1:05 before making the next call
        time.sleep(65)