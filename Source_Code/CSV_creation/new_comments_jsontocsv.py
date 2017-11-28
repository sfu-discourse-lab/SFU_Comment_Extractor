import json
from glob import glob
import os
from fuzzywuzzy import fuzz
import io
import re
import unicodecsv as csv

def process_text(old_text):
    return re.sub(r'\(In reply to:.*?--((\s\S+){1,10})?\)', '', old_text)

def nested_thread_check(nested_replies,article_id,new_article_id):
    if nested_replies:
        child_comment_counter = 0
        for replies in nested_replies:
            add_csv_sublist = []
            add_csv_sublist.append(article_id)
            add_csv_sublist.append(new_article_id+'_'+str(child_comment_counter))
            add_csv_sublist.append(rootkey) #generating IDs for child comments in replies
            add_csv_sublist.append(process_text(replies['text']))
            add_csv_sublist.append(replies['reactions'])
            add_csv_sublist.append(replies['post_time'])
            add_csv_sublist.append(replies['author'])
            add_csv_sublist.append('Yes' if 'replies' in replies else 'No')
            csv_list.append(add_csv_sublist)
            csv_cache_list.append(add_csv_sublist)
            child_comment_counter = child_comment_counter + 1
            if 'replies' in replies:
                nested_thread_check(replies['replies'],article_id,new_article_id)
    else:
        pass
csv_list = []
global_counter = 0
article_counter = 1
# to iterate through all .json files in new_comments directory 
with io.open("dummy.csv", "wb") as fs:
    writer = csv.writer(fs, encoding='utf-8')
    writer.writerow(['index1','comment1','index2','comment2','weighted_score','token_sort_score'])
    for article in glob('/Users/vkolhatk/Data/GnM_Scraped_data/New_Comments/new_comments_jsons/*.json'):
        # iterating through each article file
        csv_cache_list=[]
        with io.open(article) as data_file:    
            data = json.load(data_file)
            article_id = os.path.basename(article).split('_')[1]
        root_comment_counter = 0
        for rootkey,rootval in data.items():
            # initializing variable for numbering child comments in replies
            child_comment_counter = 0
            csv_sublist = []
            
            # appending article_id
            csv_sublist.append(article_id)
            new_article_id='source2_'+article_id+'_'+str(root_comment_counter)
            csv_sublist.append(new_article_id)
            # appending comment_id
            csv_sublist.append(rootkey)

            # appending self-explanatory field names
            csv_sublist.append(process_text(rootval['text']))
            csv_sublist.append(rootval['reactions'])
            csv_sublist.append(rootval['post_time'])
            csv_sublist.append(rootval['author'])
            # if comment has replies, set field value to 'Yes' else 'No'
            if rootval['replies']:
                csv_sublist.append('Yes')
            else:
                csv_sublist.append('No')
            # this appends all the parent comments
            csv_list.append(csv_sublist)
            csv_cache_list.append(csv_sublist)
            nested_thread_check(rootval['replies'],article_id,new_article_id)
            # Check if there are Thread comments, if yes, add them as a new row in csv

            root_comment_counter = root_comment_counter + 1
        article_counter = article_counter + 1


csv_header_list = ["article_id", "comment_counter" ,"comment_id", "text", "reactions", "post_time", "author", "replies"]

with io.open("new_comments_preprocessed_with_duplicates.csv", "wb") as f:
    writer = csv.writer(f, encoding='utf-8')
    writer.writerow(csv_header_list)
    writer.writerows(csv_list)
