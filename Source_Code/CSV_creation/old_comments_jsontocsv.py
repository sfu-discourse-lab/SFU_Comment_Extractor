import json
import csv
from glob import glob
import os
from fuzzywuzzy import fuzz
import io
import re
import unicodecsv as csv
from pprint import pprint

def get_field(comments,field):
    try:
        return comments[field]
    except:
        return None

def process_text(old_text):
    return re.sub(r'\(In reply to:.*?--(\s\S+){1,4}\)', '', old_text)

def nested_thread_check(nested_replies,article_id,new_article_id):
    if nested_replies:
        child_comment_counter = 0
        for comments in nested_replies:

            add_csv_sublist = []
            # add_csv_sublist.append(article_id)
            
            add_csv_sublist.append(new_article_id + '_' + str(child_comment_counter))
            add_csv_sublist.append(rootkey)
            add_csv_sublist.append(rootval['data_type'])
            add_csv_sublist.append(rootval['is_empty'])
            add_csv_sublist.append(get_field(comments,'ID'))
            add_csv_sublist.append(get_field(comments,'parentID'))
            add_csv_sublist.append(get_field(comments,'status'))
            add_csv_sublist.append(get_field(comments,'commentText'))
            add_csv_sublist.append(get_field(comments,'edited'))
            add_csv_sublist.append(get_field(comments,'timestamp'))
            add_csv_sublist.append(get_field(comments,'isModerator'))
            add_csv_sublist.append(get_field(comments,'threadID'))
            add_csv_sublist.append(get_field(comments,'TotalVotes'))
            add_csv_sublist.append(get_field(comments,'highlightGroups'))
            add_csv_sublist.append(get_field(comments,'moderatorEdit'))
            add_csv_sublist.append(get_field(comments,'negVotes'))
            add_csv_sublist.append(get_field(comments,'streamId'))
            add_csv_sublist.append(get_field(comments,'vote'))
            add_csv_sublist.append(get_field(comments,'descendantsCount'))
            add_csv_sublist.append(get_field(comments,'threadTimestamp'))
            add_csv_sublist.append(get_field(comments,'flagCount'))
            add_csv_sublist.append(get_field(comments,'posVotes'))
            add_csv_sublist.append(get_field(comments['sender'],'isSelf'))
            add_csv_sublist.append(get_field(comments['sender'],'loginProvider'))
            add_csv_sublist.append(get_field(comments['sender'],'name'))
            csv_list.append(add_csv_sublist)
            if 'replies' in comments:
                new_article_id = new_article_id + '_' + str(child_comment_counter)
                nested_thread_check(get_field(comments,'replies'),article_id,new_article_id)
            child_comment_counter = child_comment_counter + 1
    else:
        pass

csv_list = []
global_counter = 0
article_counter = 1
# to iterate through all .json files in new_comments directory 

for article in glob('/Users/vkolhatk/Data/GnM_Scraped_data/Old_Comments/old_comments_jsons/article*.json'):
    # iterating through each article file
    csv_cache_list=[]
    with open(article) as data_file:
    	try:
		data = json.load(data_file)
    	except:
        	continue
    root_comment_counter = 0
    for rootkey,rootval in data.items():
        article_id = 'source1_' + str(rootkey)
        # initializing variable for numbering child comments in replies
        # child_comment_counter = 0
        root_comment_counter = 0
        # appending article_id
        for comments in rootval['comments']:
            csv_sublist = []

            new_article_id= article_id + '_' + str(root_comment_counter)
            csv_sublist.append(new_article_id)

            csv_sublist.append(rootkey)
            csv_sublist.append(rootval['data_type'])
            csv_sublist.append(rootval['is_empty'])
            csv_sublist.append(get_field(comments,'ID'))
            csv_sublist.append(get_field(comments,'parentID'))
            csv_sublist.append(get_field(comments,'status'))
            csv_sublist.append(get_field(comments,'commentText'))
            csv_sublist.append(get_field(comments,'edited'))
            csv_sublist.append(get_field(comments,'timestamp'))
            csv_sublist.append(get_field(comments,'isModerator'))
            csv_sublist.append(get_field(comments,'threadID'))
            csv_sublist.append(get_field(comments,'TotalVotes'))
            csv_sublist.append(get_field(comments,'highlightGroups'))
            csv_sublist.append(get_field(comments,'moderatorEdit'))
            csv_sublist.append(get_field(comments,'negVotes'))
            csv_sublist.append(get_field(comments,'streamId'))
            csv_sublist.append(get_field(comments,'vote'))
            csv_sublist.append(get_field(comments,'descendantsCount'))
            csv_sublist.append(get_field(comments,'threadTimestamp'))
            csv_sublist.append(get_field(comments,'flagCount'))
            csv_sublist.append(get_field(comments,'posVotes'))
            csv_sublist.append(get_field(comments['sender'],'isSelf'))
            csv_sublist.append(get_field(comments['sender'],'loginProvider'))
            csv_sublist.append(get_field(comments['sender'],'name'))

            csv_list.append(csv_sublist)

            # Check if there are Thread comments, if yes, add them as a new row in csv
            nested_thread_check(get_field(comments,'replies'),article_id,new_article_id)

            root_comment_counter = root_comment_counter + 1

#         if rootval['replies']:
#             csv_sublist.append('Yes')
#         else:
#             csv_sublist.append('No')
#         # this appends all the parent comments
            
#         csv_cache_list.append(csv_sublist)
            
#     print "{}{}".format("processing article ", article_counter)
#     for indextop,i in enumerate(csv_cache_list):
#         for indexdown,m in enumerate(csv_cache_list):
#             if indexdown <= indextop:
#                 continue
#             if len(i[3])<=len(m[3])/2 or len(m[3])<=len(i[3])/2:
#                 continue
#             score = fuzz.UWRatio(i[3],m[3])
#             tsort_score = fuzz.token_sort_ratio(i[3],m[3],force_ascii=False)
#             if score>=90 or tsort_score>=90:
#                 writer.writerow([global_counter+indextop,unicode(i[3]),global_counter+indexdown,unicode(m[3]),score,tsort_score])
#     global_counter = global_counter + len(csv_cache_list)
#     article_counter = article_counter + 1


csv_header_list = ['comment_counter','article_id','data_type','is_empty','ID','parentID','status','text','edited',
                    'timestamp','isModerator','threadID','TotalVotes','highlightGroups','moderatorEdit','negVotes',
                    'streamId','vote','descendantsCount','threadTimestamp','flagCount','posVotes','sender_isSelf','sender_loginProvider','author']

with open("old_comments.csv", "wb") as f:
    writer = csv.writer(f,encoding='utf-8')
    writer.writerow(csv_header_list)
    writer.writerows(csv_list)

    # article_id
    # old : source1
    # new : source2_article_id
    #commentText -> text
    #sender_name -> author
