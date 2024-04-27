import pandas as pd
import json

# Create class for parsing the New York Times
# Article Search API JSON Responses
class JSONParse:

    def __init__(self, json_response):
        self.json = json_response
        self.article_id = self.get_article_id()
        # self.article_facts = self.get_article_facts(json_response)
        # self.authors = self.get_article_authors(json_response)

    def get_article_id(self):
        #Get the id string in the resonse
        id_string = self.json.get('_id')
        #Output example:
            # nyt://article/018efce9-c1d0-5966-9dce-d1b2fbb9e334
            # Need to keep everything after the final /
        #Find right index of /
        i = id_string.rindex('/') + 1
        id_out = id_string[i:]
        return(id_out)
    
    def get_article_facts(self):
        #Get facts for each article
        # word count, number of authors, publication date, total subjects, etc.
        # word count
        word_count = int(self.json.get('word_count'))
        #keywords
        keyword_count = len(self.json.get('keywords'))
        # number of authors
        authors = int(len(self.json.get('byline')['person']))        
        # publication_date
        pub_date = pd.to_datetime(self.json.get('pub_date')).date()
        # number of words in the headline
        headline = self.json.get('headline')['main']
        #Split whitespace to get each word and get the length of the resulting list
        headline_words = len(headline.split(' '))
        #See if the article was in print
        if set(['print_section', 'print_page']).issubset(self.json.keys()) == True:
            #If it was say so & get the page and section
            in_print = True
            print_page = int(self.json.get('print_page'))
            print_section = self.json.get('print_section')
        else:
            #If not say so and set the page and section to None
            in_print = False
            print_page = None
            print_section = None
        #news_desk
        if ('news_desk' in self.json.keys()) & (self.json.get('news_desk') not in ['', None]):
            news_desk = self.json.get('news_desk')
        else:
            news_desk = None
        #secion name
        if ('section_name' in self.json.keys()) & (self.json.get('section_name') not in ['', None]):
            section_name = self.json.get('section_name')
        else:
            section_name = None
        #article type
        if ('type_of_material' in self.json.keys()) & (self.json.get('type_of_material') not in ['', None]):
            article_type = self.json.get('type_of_material')
        else:
            article_type = None
        facts = (self.article_id, #primary key
                 pub_date, 
                 word_count, 
                 keyword_count,
                 authors, 
                 headline_words, 
                 in_print, 
                 print_page, 
                 print_section,
                 news_desk,
                 section_name,
                 article_type,
                 )
        return(facts)
    
    def get_article_authors(self):
        #Get the authors for each article
        byline_authors = self.json.get('byline')['person']
        if len(byline_authors) > 0:
            authors = [
                        (   self.article_id,
                            a.get('rank'), a.get('role'), 
                            a.get('firstname'), a.get('middlename'), 
                            a.get('lastname'), a.get('qualifier')
                        ) 
                            for a in byline_authors
                            ]
            return(authors)
        else:
            return(None)
    
    def search_article_keywords(self,subject):
        ##accepted keyword variable is name
        ## keywords - subject, organizations, glocations, persons.

        
        
        # #Get a list of each keyword dictionary object
        keyword_dict_list = self.json.get('keywords')
        
        #Create a set of all subjects when looking up name in each dictionary
        keyword_subjects = set([d.get('name') for d in keyword_dict_list])
        #If it is empty return None
        if len(keyword_dict_list) == 0:
            return(None)
        #If the subject being looked up is not in the dictionaries return None
        elif subject in keyword_subjects == False:
            return(None)
        # Else get all the info associated with the subject being searched
        # Return a list of tuples
        else:
            subject_return = [
                                (
                                 self.article_id,
                                 d.get('rank'), 
                                 d.get('name'), 
                                 d.get('value'), 
                                 d.get('major')
                                 )
                                for d in keyword_dict_list if subject in d.values()
                            ]
            return(subject_return)
    #Get the headline for each article
    def get_headline(self):
        main_headline = self.json.get('headline')['main']
        output = (self.article_id, main_headline)
        return(output)
    
    #Get the abstract for each article
    def get_absract(self):
        abstract = self.json.get('abstract')
        output = (self.article_id, abstract)
        return(output)
    
    #Get the lead paragraph for each article
    def get_lead_paragraph(self):
        paragraph = self.json.get('lead_paragraph')
        output = (self.article_id, paragraph)
        return(output)
    #For each result get the column headers for the resulting
    #dataframe
    def parsed_columns(self, table):

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