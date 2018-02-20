import os, random
import pandas as pd
import re
import sys
from shutil import copyfile


def main(article_input_dir, sample_output_dir, articles_file, comments_output_dir, comments_file):
    '''Getting sample articles'''

    files = set()

    count = pd.DataFrame.from_csv(articles_file, index_col=None, header=None)

    dir = article_input_dir
    output_dir = sample_output_dir

    for idx, row in count.iterrows():
        folder_name = dir + str(row[0])
        num_of_articles = row[1]

        for i in range(1, num_of_articles):
            file_name = random.choice(os.listdir(folder_name))
            while file_name in files:
                file_name = random.choice(os.listdir(folder_name))
            files.add(file_name)
            year_folder = output_dir + str(row[0])
            if not os.path.exists(year_folder):
                os.makedirs(year_folder)

            source = folder_name + "/" + file_name
            copyfile(source, year_folder + "/" + file_name)



    '''Getting comments from sampled articles'''

    article_ids = pd.DataFrame(columns=['article_id', 'year'])
    comments_df = pd.read_csv(comments_file)
    ids_list = []
    for root, directories, filenames, in os.walk(sample_output_dir):
        for f_name in filenames:
            path = os.path.join(root, f_name)
            year = re.search('_articles/(.+?)/', path)
            if year:
                article = {}
                article['year'] = year.group(1)
                article['article_id'] = f_name.split('.')[0]
                ids_list.append(f_name.split('.')[0])
                article_ids = article_ids.append(article, ignore_index=True)

    article_ids['article_id'] = article_ids['article_id'].str.strip()

    sampled_comments = comments_df[comments_df['article_id'].isin(ids_list)]
    article_ids['article_id'] = article_ids['article_id'].astype('str').astype('int')
    sampled_comments = pd.DataFrame.merge(sampled_comments, article_ids, on="article_id")

    for idx, articles in sampled_comments.groupby('article_id'):
        folder_name = comments_output_dir + str(articles['year'].iloc[0])
        file_name = folder_name + "/" + str(idx) + "_comments.txt"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        articles.to_csv(file_name, header=None, index=None, columns=['comment_text'])


if __name__ == "__main__":
    article_input_dir = sys.argv[1]  # ./articles/
    sample_output_dir = sys.argv[2]  # ./sampled_articles/
    articles_file = sys.argv[3]  # articles_per_year.csv

    comments_output_dir = sys.argv[4]  # ./sampled_comments/
    comments_file = sys.argv[5]  # ./CSVs/gnm_comments.csv

    main(article_input_dir, sample_output_dir, articles_file, comments_output_dir, comments_file)