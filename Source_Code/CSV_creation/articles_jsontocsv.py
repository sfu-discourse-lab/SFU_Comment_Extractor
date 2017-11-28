import unicodecsv as csv
import json
from glob import iglob
import os
import io

csv_list = []

for article in iglob('/Users/vkolhatk/Data/GnM_Scraped_data/ArticleRawData/article_data_jsons/article*.json'):
    # iterating through each article file
    with open(article) as data_file:    
        data = json.load(data_file)
        for rootkey,rootval in data.items():

            csv_sublist = []
            
            # appending article_id and other fields from json data 
            csv_sublist.append(rootkey)
            csv_sublist.append(rootval['title'])
            csv_sublist.append(''.join(rootval['article_text']))
            csv_sublist.append(rootval['article_url'])
            csv_sublist.append(rootval['author'])
            csv_sublist.append(rootval['published_date'])
            csv_sublist.append(rootval['data_type'])
            csv_list.append(csv_sublist)


csv_header_list = ["article_id", "title", "article_text", "article_url", "author", "published_date", "data_type"]

with io.open("articles.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerow(csv_header_list)
    writer.writerows(csv_list)
