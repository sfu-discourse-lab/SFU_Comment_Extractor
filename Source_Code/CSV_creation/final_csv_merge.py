########################
# Author: Kavan Shukla #
########################
import pandas as pd
import argparse

def get_arguments():
    '''
    argparse object initialization and reading input and output file paths.
    input files: new_comments_preprocessed (-i1), old_comments_preprocessed.csv (-i2), comments_to_flag.txt (-i3), comments_to_delete.txt (-i4)
    output file: final_merged_comments.csv (-o) 
    '''
    parser = argparse.ArgumentParser(description='csv file identifying duplicates between new and old comments')
    parser.add_argument('--new_comments_csv', '-i1', type=str, dest='new_comments_preprocessed', action='store',
                        #default='../../Sample_Resources/Sample_Comments_CSVs/new_comments_preprocessed.csv',
                        default=r'/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/new_comments_preprocessed.csv',
                        help="the input csv file for new_comments generated from preprocessing script")

    parser.add_argument('--old_comments_csv', '-i2', type=str, dest='old_comments_preprocessed', action='store',
                        #default='../../Sample_Resources/Sample_Comments_CSVs/old_comments_preprocessed.csv',
                        default=r'/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/old_comments_preprocessed.csv',
                        help="the input csv file for old_comments generated from preprocessing script")

    parser.add_argument('--comments_to_flag', '-i3', type=str, dest='comments_to_flag', action='store',
                        #default='../../Sample_Resources/Sample_Comments_CSVs/comments_to_flag.txt',
                        default=r'/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/comments_to_flag.txt',
                        help="the input txt file generated from duplicate_filter.py containing comment_counters to flag")

    parser.add_argument('--comments_to_delete', '-i4', type=str, dest='comments_to_delete', action='store',
                        #default='../../Sample_Resources/Sample_Comments_CSVs/comments_to_delete.txt',
                        default=r'/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/comments_to_delete.txt',
                        help="the input txt file generated from duplicate_filter.py containing comment_counters to delete")

    parser.add_argument('--final_csv', '-o', type=str, dest='final_csv', action='store',
                        #default='../../Sample_Resources/Sample_Comments_CSVs/final_merged_comments.csv',
                        default=r'/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/final_merged_comments.csv',
                        help="the output file containing both source1 and source2 comments")

    args = parser.parse_args()
    return args

def merge_sources(args):
    '''
     Given an argparse object, this module creates a dictionary of comment_counters present
     in comments_to_flag.txt as key and value as {'exact_match':[<comment_counters>],'similar':[<comment_counters>]}
     based on the weighted score and token sort score
     Concatenates the dataframes of csvs from both the sources (new and old comments)
     Adds a column 'flag' and populates it with the values of main_dict keys (where key is comment_counter)

    :param args: argparse object containing the input and output file paths as attributes

    '''
    flag_list = []
    list_of_comments_to_delete = []
    with open(args.comments_to_flag,'r') as flag:
        for f in flag.readlines():
             flag_list.append(f.strip().split(','))
                
    with open(args.comments_to_delete,'r') as comments_to_delete:
        for c in comments_to_delete.readlines():
            list_of_comments_to_delete.append(c.strip())

    main_dict = {}
    value_struct = {'exact_match':[],'similar':[]}

    for i in flag_list:
        weighted_ratio = int(i[-2])
        token_sort_ratio = int(i[-1])
        if main_dict.get(i[0]):
            if (weighted_ratio>85 and weighted_ratio<100) and (token_sort_ratio>85 and token_sort_ratio<100):
                main_dict[i[0]]['similar'].append(i[1])
            if (weighted_ratio==100) and (token_sort_ratio==100):
                main_dict[i[0]]['exact_match'].append(i[1])
        else:
            main_dict[i[0]] = value_struct
            if (weighted_ratio>85 and weighted_ratio<100) and (token_sort_ratio>85 and token_sort_ratio<100):
                main_dict[i[0]]['similar'].append(i[1])
            if (weighted_ratio==100) and (token_sort_ratio==100):
                main_dict[i[0]]['exact_match'].append(i[1])
                
    new_comments = pd.read_csv(args.new_comments_preprocessed)
    old_comments = pd.read_csv(args.old_comments_preprocessed)
    old_comments.rename(columns = {'ID':'comment_id'}, inplace = True)
    # old_comments.rename(columns = {'timestamp':'post_time'}, inplace = True)
                
    merging_final = pd.concat([old_comments, new_comments])

    merging_final['flags'] = """{'exact_match':[],'similar':[]}"""

    ''' 
    following line of commented code will delete the comments from the final csv 
    based on the comment_counters in comments_to_delete.txt
    '''
    # merging_final = merging_final.query('comment_counter not in @list_of_comments_to_delete')

    for row in merging_final.itertuples():
        if row.comment_counter in main_dict:
            merging_final.set_value(row.Index, 'flags', str(main_dict.get(row.comment_counter)))

    return merging_final

if __name__=="__main__":
    args = get_arguments()
    merged_comments = merge_sources(args)
    merged_comments.to_csv(args.final_csv, index=False)