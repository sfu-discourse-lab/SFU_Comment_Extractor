########################
# Author: Kavan Shukla #
########################
import pandas as pd
import argparse
import re

def get_arguments():
    '''
    argparse object initialization and reading input and output file paths.
    input file: merged_old_new_duplicates.csv (-i)
    output files: comments_to_flag.txt and comments_to_delete.txt (-o1 anb -o2) 
    '''
    parser = argparse.ArgumentParser(description='csv file identifying duplicates between new and old comments')
    parser.add_argument('--merged_csv', '-i', type=str, dest='merged_old_new_duplicates', action='store',
                        #default='../../Sample_Resources/Sample_Comments_CSVs/merged_old_new_duplicates.csv',
                        default=r'/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/merged_old_new_duplicates.csv',
                        help="the input csv file generated from duplicate_identification")

    parser.add_argument('--output_comments_to_flag', '-o1', type=str, dest='comments_to_flag', action='store',
                        #default='../../Sample_Resources/Sample_Comments_CSVs/comments_to_flag.txt',
                        default=r'/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/comments_to_flag.txt',
                        help="the output file containing the comments to flag as exact_match or similar in the final csv")

    parser.add_argument('--output_comments_to_delete', '-o2', type=str, dest='comments_to_delete', action='store',
                        #default='../../Sample_Resources/Sample_Comments_CSVs/comments_to_delete.txt',
                        default=r'/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/comments_to_delete.txt',
                        help="the output file for writing comment_counter for the comments to be deleted")

    args = parser.parse_args()
    return args

def longest(row):
    '''
    :param row: pandas dataframe row object in namedtuple format
     Given a pandas dataframe row namedtuple, this module returns the comment_counter for the comment text with highest length.
    '''
    if len(row.comment1) > len(row.comment2):
        return row.comment_counter2
    else:
        return row.comment_counter1

def filter_duplicates(args):
    '''
    :param args: argparse object containing the input and output file as attributes
     Given an argparse object, this module creates a pandas dataframe from the input csv and filters the 
     duplicates in two text files and outputs comments_to_delete and comments_to_flag based on the algorithm below. 

    1. If the same source
        a) different parent 
            KEEP BOTH
        b) same parent and threshold > 85 (Confident about the comment being a duplicate. So a low threshold is OK.) 
            KEEP THE LONGER ONE

    2. If different source
        Flag source 1 comment in the final csv: 'Potential duplicate (similar or exact_match) of comment_id'

    '''
    duplicates = pd.read_csv(args.merged_old_new_duplicates)

    with open(args.comments_to_delete,"w") as to_delete:
        with open(args.comments_to_flag,"w") as to_flag:
            ########Duplicate Removal Algorithm######
            for row in duplicates.itertuples():
                if row.comment_counter1[:7] == row.comment_counter2[:7]:
                    if row.comment_counter1.count('_') == row.comment_counter2.count('_') and \
                        re.findall('_(.*?)(?=\_)', row.comment_counter1)[-1] == re.findall('_(.*?)(?=\_)', row.comment_counter2)[-1]:
                        to_delete.write(longest(row)+'\n')
                    else:
                        continue
                else:
                    comment_flag = (row.comment_counter1,row.comment_counter2)
                    to_flag.write(row.comment_counter1+','+row.comment_counter2+','+str(row.weighted_score) + ','+str(row.token_sort_score)+'\n')

if __name__=="__main__":
    args = get_arguments()
    filter_duplicates(args)