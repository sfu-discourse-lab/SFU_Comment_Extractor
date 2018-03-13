import pandas as pd
import re
import ast
import multiprocessing as mp
from multiprocessing import cpu_count
import sys


def check_match(thread_df):
    pat = "source2_\d+_\d+"
    for i, row in thread_df.iterrows():
        duplicate = ast.literal_eval(row.duplicate_flag)
        if not duplicate['exact_match']:
            return False
    return re.findall(pat, " ".join(duplicate['exact_match']))


def thread_length(orig_length, comment_id, threads_df, orig_comment_id):
    orig_df = threads_df[threads_df.comment_counter.str.contains(orig_comment_id + "$|" + orig_comment_id + "_")]
    for id in comment_id:
        counter = 0
        temp_df = threads_df[threads_df.comment_counter.str.contains(id + "$|" + id + "_")]
        if len(temp_df) == orig_length:
            for i, row in orig_df.iterrows():
                match_list = ast.literal_eval(row.duplicate_flag)
                if re.findall(id + "$|" + id + "_", " ".join(match_list['exact_match'])):
                    counter += 1
            if counter == orig_length:
                return id
    return False


def parallelize(data, func):
    cores = cpu_count()

    df_list = []
    for i, df_article_id in data.groupby('article_id'):
        df_list.append(df_article_id)
    print("Dataframes list prepared.")
    pool = mp.Pool(cores)
    data = pd.concat(pool.map(func, df_list))
    pool.close()
    pool.join()
    return data


def remove_duplicate_threads(threads_df):

    pattern = "source1_\d+_\d+$"

    source1_df = threads_df[threads_df['comment_counter'].str.contains(pattern)]
    root_comments = list(source1_df.comment_counter)

    for comment in root_comments:
        thread = threads_df[threads_df.comment_counter.str.contains(comment + "$|" + comment + "_")]
        if thread.empty:
            continue
        match = check_match(thread)
        if match:
            match_id = thread_length(len(thread), match, threads_df, comment)
            if match_id:
                threads_df = threads_df[~threads_df['comment_counter'].str.contains(match_id + "$|" + match_id + "_")]

    return threads_df


def main():

    articles_df = pd.DataFrame.from_csv(sys.argv[1], encoding="ISO-8859-1", index_col=None)

    df_processed = parallelize(articles_df, remove_duplicate_threads)
    df_processed.to_csv("duplicates_removed.csv", index=False)


if __name__ == "__main__":
    main()
