__author__ = 'Varada Kolhatkar'
import pandas as pd
import argparse
import operator
import pickle
import sys
from timeit import default_timer as timer

def get_arguments():
    parser = argparse.ArgumentParser(description='Write csv files for crowd annotation')
    parser.add_argument('--input_csv', '-i', type=str, dest='input_csv', action='store',
                        #default=r'/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/merged_old_new_duplicates.csv',
                        default=r'../../Sample_Resources/Sample_Comments_CSVs/sample_merged_duplicates.csv',
                        help="the input csv file")

    parser.add_argument('--new_comments', '-nc', type=str, dest='new_comments', action='store',
                        #default=r'/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/new_comments_preprocessed.csv',
                        default=r'../../Sample_Resources/Sample_Comments_CSVs/sample_new_comments_preprocessed.csv',
                        help="the new comments csv file")


    parser.add_argument('--old_comments', '-oc', type=str, dest='old_comments', action='store',
                        #default=r'/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/old_comments_preprocessed.csv',
                        default=r'../../Sample_Resources/Sample_Comments_CSVs/sample_old_comments_preprocessed.csv',
                        help="the old comments csv file")

    parser.add_argument('--pickle_path', '-p', type=str, dest='pickle_path', action='store',
                        #default=r'/Users/vkolhatk/Data/GnM_CSVs/python_pickling/sample_comment_clusters.p',
                        default=r'../../Sample_Resources/Sample_Comments_CSVs/sample_comment_clusters.p',
                        help="the path to pickle comment clusters")

    parser.add_argument('--threshold', '-t', type=int, dest='threshold', action='store',
                        default=87,
                        help="the threshold to remove comments")

    parser.add_argument('--file_with_ids_to_remove', '-o', type=str, dest='remove_ids_file', action='store',
                        #default='/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/sample_ids_to_remove.csv',
                        default=r'../../Sample_Resources/Sample_Comments_CSVs/sample_ids_to_remove.csv',
                        help="the output file containing ids to remove")

    args = parser.parse_args()
    return args


def find_and_update_cluster(id1, id2):
    '''
    :param id1: (str)
    :param id2: (str)
    :return: Given comment counters of similar or identical comments, put the comments in the right comment
          clusters if they are not already there. The function does not return anything but updates the global variable
          comment_clusters.
    '''
    for cluster in comment_clusters:
        if id1 in cluster and id2 in cluster:
            # Both ids are in the cluster. No need to update
            return
        elif id1 in cluster:
            cluster.append(id2)
            return
        elif id2 in cluster:
            cluster.append(id1)
            return

    comment_clusters.append([id1, id2])

def get_comment_clusters(df, threshold):
    '''
    :param df: (pandas.DataFrame)
    :param threshold: (int)
    :return: Given a pandas.DataFrame with merged duplicates from old and new comments and a threshold, this function
     gets the clusters and returns
    '''
    for index, row in df.iterrows():
        print('working on index:', index)
        if (row['weighted_score'] + row['token_sort_score'])/2 < threshold:
            continue

        find_and_update_cluster(row['comment_counter1'], row['comment_counter2'])

def get_potential_duplicates_from_cluster(cluster, new_comment_id_len_dict, old_comment_id_len_dict):
    '''
    :param cluster: (list)
    :param new_comment_id_len_dict: (dict)
    :param old_comment_id_len_dict: (dict)
    :return: (list) Given a comment cluster, cluster, and dictionaries with comment counter and comment lengths,
        new_comment_id_len_dict, old_comment_id_len_dict, this function selects the most representative comment
        from the cluster and returns a list of comment counters to be removed.
    '''
    score = 0
    # source1 gets more weight compared to source2
    source1_weight = 0.60
    source2_weight = 0.40
    comment_id_score_dict = {}

    # Also, higher-level comments have a better chance of being chosen as the representative ones.
    depth_map = {0:10, 1:8, 2:6, 3:4, 4:2, 5:1, 6:0}

    try:
        for comment_id in cluster:
            depth = comment_id.count('_') - 2
            if depth > 6:
                depth = 6

            if comment_id.startswith('source1'):
                comment_id_score_dict[comment_id] = source1_weight * old_comment_id_len_dict[comment_id] + depth_map[depth]
            elif comment_id.startswith('source2'):
                comment_id_score_dict[comment_id] = source2_weight * new_comment_id_len_dict[comment_id] + depth_map[depth]

        sorted_x = sorted(comment_id_score_dict.items(), key=operator.itemgetter(1),reverse=True)
        representative_comment = sorted_x[0][0]
        to_remove = [comment_counter for comment_counter in cluster if comment_counter != representative_comment]
        return to_remove
    except:
        print('Returning the whole cluster to remove')
        print('Cluster: ', cluster)
        print('-------------')
        return cluster


def get_length(text):
    '''
    :param text:
    :return: the length of the text in characters
    '''
    return len(str(text))

def identify_ids_to_remove():
    '''
    :return:
    '''
    ids_to_remove = []
    new_comments_df = pd.read_csv(args.new_comments)
    new_comments_df = new_comments_df.dropna(axis=0,how='any')
    new_comments_df['length'] = new_comments_df['text_preprocessed'].apply(get_length)
    new_comment_id_len_dict = dict(zip(new_comments_df.comment_counter, new_comments_df.length))

    old_comments_df = pd.read_csv(args.old_comments)
    old_comments_df['length'] = old_comments_df['text_preprocessed'].apply(get_length)
    old_comment_id_len_dict = dict(zip(old_comments_df.comment_counter, old_comments_df.length))

    for cluster in comment_clusters:
        remove_ids = get_potential_duplicates_from_cluster(cluster, new_comment_id_len_dict, old_comment_id_len_dict)
        ids_to_remove.extend(remove_ids)

    df = pd.DataFrame({'comment_counters_to_remove': ids_to_remove})
    df.to_csv(args.remove_ids_file, index=False)
    print('Remove ids written in file: ', args.remove_ids_file)


def explore_cluster(cluster, output_csv):
    '''
    :param cluster: (list)
    :param output_csv: (str)
    :return: Given a comment cluster writes the comments in the given cluster in the output_csv.
    '''

    new_comments_df = pd.read_csv(args.new_comments)
    new_comments_df = new_comments_df.dropna(axis=0,how='any')

    old_comments_df = pd.read_csv(args.old_comments)

    ndf_subset = new_comments_df[new_comments_df['comment_counter'].isin(cluster)]
    odf_subset = old_comments_df[old_comments_df['comment_counter'].isin(cluster)]

    print('Clustered comments:')
    print(ndf_subset.columns.values)
    print(odf_subset.columns.values)
    ndf_subset_subset = ndf_subset[['article_id', 'comment_counter', 'author','text_preprocessed']]
    odf_subset_subset = odf_subset[['article_id', 'comment_counter', 'author', 'text_preprocessed']]
    df_concat = ndf_subset_subset.append(odf_subset_subset)
    df_concat.to_csv(output_csv, index = False)

if __name__=="__main__":
    args = get_arguments()
    start = timer()
    print('Start time: ', start)
    df = pd.read_csv(args.input_csv)
    comment_clusters = []
    get_comment_clusters(df, args.threshold)
    pickle.dump(comment_clusters, open(args.pickle_path,'wb'))
    print('Comment clusters created and pickled at path: ', args.pickle_path)
    comment_clusters = pickle.load(open(args.pickle_path,'rb'))
    print('Number of comment clusters: ', len(comment_clusters))
    print(comment_clusters)
    identify_ids_to_remove()
    end = timer()
    print('Total time taken: ', end-start)

    #explore_cluster(['source1_10218956_16', 'source1_10218956_19_0', 'source2_10218956_18_0', 'source2_10218956_26'], '/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/test.csv')


