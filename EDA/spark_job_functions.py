from pyspark.sql import SparkSession
from pyspark.sql import Window
from pyspark.sql import functions as f
from pyspark.sql.types import *
from itertools import chain

#Function to extend lists of tuples returned from JSON Parsing
def extend_list(list_name, function_result):
    #If the function result isn't None extend the list
    if function_result != None:
        list_name.extend(function_result)
    #Else pass
    else:
        pass

# Function to get the table headers for the appropriate dataframe
def get_table_headers(table):

    table_col_dict = {
        'facts':['article_id', 'publication_date',
                            'word_count', 'total_keywords',
                            'total_authors', 'words_in_headline',
                            'in_print', 'print_page', 'print_section',
                            'news_desk', 'section_name', 'article_type'],
        'authors':['article_id', 'rank', 'role',
                            'firstname', 'middlename', 'lastname', 'qualifier'],
        'subjects':['article_id', 'rank', 'name', 'value', 'major'],
        'text':['article_id', 'text']
    }

    headers = table_col_dict.get(table)
    return(headers)

# Create primary key for places_and_things, authors, and people dataframes
def create_primary_key(df, key_name, article_id, order_col):
    #Create window function to partition by id and order by rank
    window = Window().partitionBy(article_id).orderBy(order_col)    
    #Row number
    df = df.withColumn(key_name, f.row_number().over(window))
    #Divide each row number by 1000 to get a decimal representation
    df = df.withColumn(key_name, f.col(key_name) / 1000)
    #Add the decimal to the id column (primary key for fact dataframe) to create a logical
    #Key representation
    df = df.withColumn(key_name, f.col(article_id) + f.col(key_name))
    return(df)

def standardize_text(clean_df, clean_col, dim_df):
    #clean_df = the dataframe to be cleaned
    #clean_col = the column to be cleaned
    #dim_df = the dimensional table to clean with
    #replace any 'None' strings with None type
    clean_df = clean_df.withColumn(clean_col, f.when(clean_df[clean_col] == 'None', None).otherwise(clean_df[clean_col]))
    #Get distinct values where not null
    distincts = clean_df.where(clean_df[clean_col].isNotNull()).select(clean_df[clean_col]).distinct()
    #Get values that aren't in the dimensional tables
    distincts = distincts.join(dim_df, [clean_col], how = 'left')
    #get the id column from the dimensional table
    id_col = f'{clean_col}_id'
    dirty_text = distincts.where(distincts[id_col].isNull()).select(distincts[clean_col].alias('dirty_text'))
    #Cross join and calculate levenshtein distance
    dirty_text = dirty_text.crossJoin(dim_df).select(['dirty_text', clean_col])
    dirty_text = dirty_text.withColumn('levenshtein', f.levenshtein('dirty_text', clean_col))

    #Get min levenshtein distance for each dirty text
    #Min = best match
    min_lev = dirty_text.groupBy('dirty_text').agg(f.min('levenshtein').alias('levenshtein'))
    dirty_text = dirty_text.join(min_lev, ['dirty_text' , 'levenshtein'])

    #In case there are no good matches use row number and grab first one
    window = Window().partitionBy('dirty_text').orderBy('dirty_text')
    dirty_text = dirty_text.withColumn('row_num', f.row_number().over(window))
    dirty_text = dirty_text.where(dirty_text['row_num']== 1).select(['dirty_text', clean_col])
    text_mapping = {row['dirty_text']:row[clean_col] for row in dirty_text.rdd.collect()}
    clean_df = clean_df.replace(text_mapping, subset = [clean_col])
    return(clean_df)

