﻿
# News - The New York Times

##  **Purpose**

The _main_ purpose of this repository is to showcase my use of more advanced analytical tools like Apache Spark, Apache Iceberg, and TensorFlow to produce end-to-end data engineering and machine learning pipelines. [The New York Times provides a host of API's](https://developer.nytimes.com/apis) that make this possible. For this project, I've chosen to focus on their [article search api](https://developer.nytimes.com/docs/articlesearch-product/1/overview) to perform a sentiment analysis on article headlines since the year 2000 when the subject of the article focuses on one of the 50 states in the United States, and compare how or if the sentiment of how those text fields are written differ among various states.

## **Results / Data Analysis**

In my dataset, I originally targeted 5000 total headlines (100 per state), but during the API call I found that there was some overlap among states (API returning the same article info for multiple state calls), so our final dataset has 4693 unique headlines to analyze. Some interesting results were noticed.

### **Total Average Sentiment Score**

According to my model, the average sentiment score across all states is **0.236**. With 1 being a positive headline and 0 being a negative, we can say that this means the headlines in our data are mostly negative.

### **Average Headline Sentiment by State**

When we look at the headline sentiment by each state (the state is a main subject in the article the headline is about) we see a few interesting results.

1. The state of New York is _by far_ the most negatively written about state. An assumption can be made that because the New York Times' writers are actively experiencing what they're writing about there, and because the headlines across all states are mostly negative, that the negative intensity in New York is greater than in other areas.

2. We see the Southeastern region of the US scores more negatively than other regions, and can associate a negative bias towards this region in general.

3. Illinois and Washington skew more negatively than other established liberal states.

![sentiment_map](https://github.com/samlawson1/news/assets/52726406/ba284363-eaa5-480c-80bf-dc76b63282f9)


### **Headline sentiment when the article is about particular people**

The data allows us to look at how often certain people are written about and _potentially_ characterized in an article. While the article isn't necesarrily about them individually, it can give us an idea of how the New York Times characterizes them by and large. It is probably unsurprising that the most written about people in our dataset are either U.S. Presidents or Presidential candidates, with Donald Trump being the most frequently written about person at 209 articles.

What is surprising (at least to me) is that Barack Obama has the lowest sentiment score out of the top 10 most written about people.

![most_written_about_people](https://github.com/samlawson1/news/assets/52726406/c22db91d-ce15-4d16-960a-679434cfc9ab)


### **News Desk sentiment**

Lastly, I wanted to look at if particular news desks wrote more positive or more negative headlines. To be considered, a news desk needed to have at least 25 articles in the dataset.

We can see that the Style, Upshot, and Sports desks write the most positive headlines and perhaps surprisingly the Washington and Op-Ed desks round out the top 5.

![positive_sentiment_news_desks](https://github.com/samlawson1/news/assets/52726406/be1cd6a1-26f8-4a97-818d-a1d85dac4d1f)


On the negative side of things, Food, Arts, Foreign, Flight, and Science have the most negative headlines.

![negative_sentiment_news_desks](https://github.com/samlawson1/news/assets/52726406/63b0017e-d39f-40b4-b0d4-bcf83829e74d)


##  **Process Overview**

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

I am using a text classification model to perform a sentiment analysis on the headlines, abstracts, and lead paragraphs for each New York Times article in order to see if there is any bias among the states.

To train and test my model, I chose to utilzed the [A Million News Headlines](https://www.kaggle.com/datasets/therohk/million-headlines) dataset from Kaggle, which is unlabeled. So the first step to train the model would be to label the data. To do this, I utilzed the [afin](https://pypi.org/project/afinn/) package in python to label the text fields and then randomly filtered the dataset from over 1.2 Million rows to 200,000 rows with a 50/50 split of positive and negative labels.

**I used Google Colab is for developing and training my model. Instead of figuring out what the appropriate packages, dependencies, and infrastructure
was necessary to do what I wanted locally on my own computer (and waiting a long time to see if the model was trained correctly), Google Colab allowed me to save
an insane amount of time and frustration!**

For the scope of this project I chose to stick with a single-label text classification model, but in the future I would like to try and utilize the AFinn score in some way.

Once the model was built, it was tested with a 96% accuracy!

![image](https://github.com/samlawson1/news/assets/52726406/a9861be7-7bbb-47cd-aed9-29a208491a37)

### Part 4 - NYT Article Text Classification

Once my model was trained to my satisfaction scoring the article text was as simple as uploading my data to my Google Drive and using Google Colab to score the text! Project complete!










