import pandas as pd
import argparse
import operator
import pickle
from timeit import default_timer as timer

def get_arguments():
    parser = argparse.ArgumentParser(description='Write csv files for crowd annotation')
    parser.add_argument('--new_comments_csv', '-n', type=str, dest='new_comments_csv', action='store',
                        #default=r'/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/new_comments_preprocessed.csv',
                        default=r'../../Sample_Resources/Sample_Comments_CSVs/sample_new_comments_preprocessed.csv',
                        help="the new comments csv file")

    parser.add_argument('--old_comments_csv', '-l', type=str, dest='old_comments_csv', action='store',
                        #default=r'/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/old_comments_preprocessed.csv',
                        default=r'../../Sample_Resources/Sample_Comments_CSVs/sample_old_comments_preprocessed.csv',
                        help="the old comments csv file")

    parser.add_argument('--mergerd_comments_csv', '-m', type=str, dest='mergerd_comments_csv', action='store',
                        #default=r'/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/merged_comments_preprocessed.csv',
                        default=r'../../Sample_Resources/Sample_Comments_CSVs/sample_merged_comments_preprocessed.csv',
                        help="the merged comments csv file")

    parser.add_argument('--ids_to_remove_file', '-k', type=str, dest='ids_to_remove_file', action='store',
                        #default='/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/ids_to_remove.csv',
                        default=r'../../Sample_Resources/Sample_Comments_CSVs/sample_ids_to_remove.csv',
                        help="the list of ids to keep")

    parser.add_argument('--length_th', '-t', type=int, dest='length_th', action='store',
                        default=10,
                        help='Length (in chars) threshold for comments')

    parser.add_argument('--gnm_csv', '-o', type=str, dest='gnm_csv', action='store',
                        #default=r'/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/gnm_comments.csv',
                        default=r'../../Sample_Resources/Sample_Comments_CSVs/tiny_sample_gnm_comments.csv',
                        help="the final G&M comments csv file")

    args = parser.parse_args()
    return args

def post_processing_comments(gnm_df):
    '''
    :param df:
    :return:
    '''
    gnm_df['text_preprocessed'] = gnm_df['text_preprocessed'].astype('str')
    # Get rid of rows with null comments
    gnm_df = gnm_df.dropna(axis=0, how='all')
    # Get rid of rows with comments < this comment did not meet civility standards > and

    # Rename text_preprocessed column to comment_text
    gnm_df.rename(columns={'text_preprocessed': 'comment_text'}, inplace=True)

    # Get rid of rows with comments containing less than x characters
    gnm_df_filtered = gnm_df[gnm_df['comment_text'].str.len() >= args.length_th]


    gnm_df_final = gnm_df_filtered[~gnm_df_filtered['comment_text'].str.startswith(("< this comment did not meet civility standards >", "This comment has been deleted", "< user deleted >"))]
    return gnm_df_final
    #gnm_df_final.to_csv(args.gnm_csv, index=False)

def merge_comments(new_comments_df, old_comments_df):
    '''
    :return:
    '''

    new_comments_df = new_comments_df.dropna(axis=0,how='all')
    print(new_comments_df.columns.values)

    print(old_comments_df.columns.values)
    old_comments_df.rename(columns={'ID': 'comment_id'}, inplace=True)
    result_df = pd.concat([old_comments_df, new_comments_df], axis=0).reset_index()
    cols = ['article_id', 'comment_counter', 'comment_id', 'author', 'post_time', 'timestamp', 'text_preprocessed', 'reactions',
            'replies', 'TotalVotes', 'negVotes','posVotes']
    result_df.to_csv(args.mergerd_comments_csv, columns=cols, index = False)
    print('Merged comments written at: ', args.mergerd_comments_csv)
    print(result_df.columns.values)

def filter_csv(input_csv, column, ids_to_remove):
    '''
    :param input_csv:
    :param column:
    :param ids_to_remove:
    :return:
    '''
    df = pd.read_csv(input_csv, dtype=str)
    #df = df[~df[column].str.startswith(ids_to_remove)]
    print('Number of ids to remove: ', len(ids_to_remove))
    print('Number of rows in the dataframe: ', len(df))
    df = df[~df[column].isin(ids_to_remove)]
    gnm_final = post_processing_comments(df)
    gnm_final.to_csv(args.gnm_csv, index=False)
    print('The final csv written in: ', args.gnm_csv)
    print('Length of gnm csv: ', len(df))
    print('Length of post-processed gnm csv: ', len(gnm_final))

if __name__=="__main__":
    args = get_arguments()
    start = timer()
    print('Start time: ', start)
    new_comments_df = pd.read_csv(args.new_comments_csv)
    old_comments_df = pd.read_csv(args.old_comments_csv)
    merge_comments(new_comments_df, old_comments_df)
    #ids_to_remove  = ('source1_10012655_10_0','source2_10012655_9_0')
    df_ids = pd.read_csv(args.ids_to_remove_file)
    ids_to_remove  = df_ids['comment_counters_to_remove'].tolist()
    filter_csv(args.mergerd_comments_csv, 'comment_counter', ids_to_remove)

    end = timer()
    print('Total time taken: ', end-start)

    #identify_ids_to_keep()
    #df.to_csv('/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/sample_merged_old_new_duplicates.csv',index=False)




