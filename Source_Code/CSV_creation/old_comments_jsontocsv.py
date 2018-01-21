import json
import csv
from glob import glob
import os
import re
import csv
import argparse

def get_arguments():
    '''
    argparse object initialization and reading input and output file paths.
    input files: input path to location where old comments json files are stored (-i)
    output file: the output csv file containing old comments (-o) 
    '''
    parser = argparse.ArgumentParser(description='csv file generated from old comments json files')
    parser.add_argument('--old_comments_jsons', '-i', type=str, dest='old_comments_json_files', action='store',
                        default=r'/Users/vkolhatk/Data/GnM_Scraped_data/Old_Comments/old_comments_jsons/*.json',
                        help="the input path to location where old comments json files are stored")

    parser.add_argument('--output_csv', '-o', type=str, dest='output_csv', action='store',
                        #default='../../Sample_Resources/Sample_Comments_CSVs/old_comments.csv',
                        default=r'/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/old_comments.csv',
                        help="the output csv file containing old comments")

    args = parser.parse_args()
    return args

def json_to_csv(input_json_files,output_csv):
    '''
    takes in input location of json files and cretes csv by iterating on all the json files
    input files: input path to location where old comments json files are stored
    output file: the output csv file containing old comments
    '''
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
                thread_article_id = new_article_id
                if 'replies' in comments:
                    thread_article_id = thread_article_id + '_' + str(child_comment_counter)
                    nested_thread_check(get_field(comments,'replies'),article_id,thread_article_id)
                child_comment_counter = child_comment_counter + 1
        else:
            pass

    csv_list = []
    global_counter = 0
    article_counter = 1
    # to iterate through all .json files in new_comments directory 

    for article in glob(input_json_files):
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


    csv_header_list = ['comment_counter','article_id','data_type','is_empty','ID','parentID','status','text','edited',
                        'timestamp','isModerator','threadID','TotalVotes','highlightGroups','moderatorEdit','negVotes',
                        'streamId','vote','descendantsCount','threadTimestamp','flagCount','posVotes','sender_isSelf','sender_loginProvider','author']

    with open(output_csv, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(csv_header_list)
        writer.writerows(csv_list)

if __name__=="__main__":
    args = get_arguments()
    json_to_csv(args.old_comments_json_files,args.output_csv)