import pandas as pd
from fuzzywuzzy import fuzz
import csv
import argparse


def get_arguments():
    parser = argparse.ArgumentParser(description='csv file identifying duplicates between new and old comments')
    parser.add_argument('--new_comments_csv', '-i1', type=str, dest='new_comments_csv', action='store',
                        default='../../Sample_Resources/Sample_Comments_CSVs/new_comments_preprocessed.csv',
                        help="the input new comments csv file")

    parser.add_argument('--output_csv', '-o', type=str, dest='output_csv', action='store',
                        default='../../Sample_Resources/Sample_Comments_CSVs/merged_duplicates.csv',
                        help="the output csv file containing duplicate pairs")

    parser.add_argument('--old_comments_csv', '-i2', type=str, dest='old_comments_csv', action='store',
                        default='../../Sample_Resources/Sample_Comments_CSVs/old_comments.csv',
                        help="the input old comments csv file")

    args = parser.parse_args()
    return args

def identify(groupby_articles, args):
    '''
    :param groupby_articles: pandas groupbyobject by article_id
    :param args: argparser object
     Given a pandas groupby object, this module identifies duplicates and write the duplicate pairs to output csv mentioned in argparse.output_csv
     doing the word segmentation.
    '''
    csv_header_list = ['article_id','author','comment_counter1','comment1','comment_counter2','comment2','weighted_score','token_sort_score']
    with open(args.output_csv,'w',newline='',encoding='utf-8') as duplicatecsv:
        writer = csv.writer(duplicatecsv)
        writer.writerow(csv_header_list)

        for arts in range(0,len(groupby_articles)):
            for i in groupby_articles[arts].itertuples():
                for m in groupby_articles[arts].itertuples():
                    if i.author!=m.author:
                        continue
                    if m.Index <= i.Index:
                        continue
                    try:
                        if len(i.text.decode('utf-8'))<=len(m.text.decode('utf-8'))/2 or len(m.text.decode('utf-8'))<=len(i.text.decode('utf-8'))/2:
                            continue
                        if any(match == "< this comment did not meet civility standards >" or match == "This comment has been deleted" for match in [i.text,m.text]):
                            continue
                        score = fuzz.UWRatio(i.text.decode('utf-8'),m.text.decode('utf-8'))
                        tsort_score = fuzz.token_sort_ratio(i.text.decode('utf-8'),m.text.decode('utf-8'),force_ascii=False)
                        if score>=90 or tsort_score>=90:
                            writer.writerow([i.article_id,i.author,i.comment_counter,i.text,m.comment_counter,m.text,score,tsort_score])
                    except:
                        if len(str(i.text))<=len(str(m.text))/2 or len(str(m.text))<=len(str(i.text))/2:
                            continue
                        if any(match == "< this comment did not meet civility standards >" or match == "This comment has been deleted" for match in [i.text,m.text]):
                            continue
                        score = fuzz.UWRatio(str(i.text),str(m.text))
                        tsort_score = fuzz.token_sort_ratio(str(i.text),str(m.text),force_ascii=False)
                        if score>=90 or tsort_score>=90:
                            writer.writerow([i.article_id,i.author,i.comment_counter,i.text,m.comment_counter,m.text,score,tsort_score])
            #print(arts)

if __name__=="__main__":
    args = get_arguments()
    
    old = pd.read_csv(args.old_comments_csv)
    new = pd.read_csv(args.new_comments_csv)
    #print(new.head())

    oldd = old.filter(['comment_counter','article_id','text','author'], axis=1)
    neww = new.filter(['comment_counter','article_id','text_preprocessed','author'], axis=1)
    neww.rename(columns = {'text_preprocessed':'text'}, inplace = True)
    merged_comments = pd.concat([oldd,neww]).reset_index()
    #print(merged_comments.tail())

    article_groups = merged_comments.groupby('article_id')
    groupby_articles = [article_groups.get_group(x) for x in article_groups.groups]
    identify(groupby_articles,args)
