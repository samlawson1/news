﻿
# News - The New York Times

##  **Purpose**

The _main_ purpose of this repository is to showcase my use of more advanced analytical tools like Apache Spark, Apache Iceberg, and TensorFlow to produce end-to-end data engineering and machine learning pipelines. [The New York Times provides a host of API's](https://developer.nytimes.com/apis) that make this possible. For this project, I've chosen to focus on their [article search api](https://developer.nytimes.com/docs/articlesearch-product/1/overview) to perform a sentiment analysis on article headlines, abstracts, and lead paragraphs when the subject of the article focuses on one of the 50 states in the United States, and compare how or if the sentiment of how those text fields are written differ among various states.
##  **Overview**

### **Tools & Languages Used:**

- [Apache Spark](https://spark.apache.org/)
- [Apache Iceberg](https://iceberg.apache.org/)
- [TensorFlow](https://www.tensorflow.org/)
- [Docker](https://www.docker.com/)
- [Python](https://www.python.org/)
- [NoSQL](https://en.wikipedia.org/wiki/NoSQL)
- [SQL](https://en.wikipedia.org/wiki/SQL)

### Part 1 - Data Collection

To collect the data, a basic python script is all that is needed to call the API and store the responses. Certain filters are necessary to meet the purpose of the project, which are:

- Filtering on The New York Times as the source
- Only including articles since January 1st, 2000
- Filtering on a specific state that is part of the article subjects
- Calling the API 10 times per state. The API is paginated, with 10 results per response. We can expect 100 articles for each state.

Given the above criteria, the following function was created.

```python
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
```


### Part 2- Data Engineering

The first step was to structure the JSON requests into a tabular format. For this, I created a python Class for some object-oriented programming.

I was interested in utilizing Apache Iceberg to get used to its configuration and functionality, so decided to use Apache Spark to create the tables and write them to an Iceberg data lake, as it is easy to integrate the two tools with one another. 

For my schema design, I went with a snowflake style schema with the following tables:

    1. article_ids
    - a column with the original hash article_id value and a column for a created integer fact_id that would be used as the primary key. 
    2. facts
    - facts about the article: publication date, word count, if it was in print, etc
    3. subject_people
    - people listed as keywords for in an article
    4. subject_others
    - organizations, locations, and subjects listed as keywords in an article
    5. authors
    - The authors of an article
    6. dim_article_types
    - dimensional table with ID's for the type of article written (Op-Ed, News, Editorial, etc.)
    7. dim_news_desks
    - dimensional table with ID's for the news desk that wrote the article (Arts, Fashion, Sports, etc.)
    8. dim_section_names
    - dimensional table with ID's for the section that wrote the article (National, Opinion, Sports, etc0
    9. dim_subject_ids
    - dimensional table with ID's for the subject categories (persons, glocations, organizations, subject)

![NYT_ICEBERG_ERD](https://github.com/samlawson1/news/assets/52726406/db854fe6-66b9-4bad-b6e7-1605f8644b98)



### Part 3 - TensorFlow Machine Learning Model Development

**The model has been developed and tested!**

I am using a text classification model to perform a sentiment analysis on the headlines, abstracts, and lead paragraphs for each New York Times article in order to see if there is any bias among the states.

To train and test my model, I chose to utilzed the [A Million News Headlines](https://www.kaggle.com/datasets/therohk/million-headlines) dataset from Kaggle, which is unlabeled. So the first step to train the model would be to label the data. To do this, I utilzed the [afin](https://pypi.org/project/afinn/) package in python to label the text fields and then randomly filtered the dataset from over 1.2 Million rows to 200,000 rows with a 50/50 split of positive and negative labels.

For the scope of this project I chose to stick with a single-label text classification model, but in the future I would like to try and utilize the AFinn score in some way.

Once the model was built, it was tested with a 95% accuracy!

![image](https://github.com/samlawson1/news/assets/52726406/2f94ac14-fafb-4c20-ba82-1e510ffd6e11)


### Part 4 - NYT Article Text Classification

**In Progress - Stay Tuned!**










