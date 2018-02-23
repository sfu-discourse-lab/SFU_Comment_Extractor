import pandas as pd
import os
import codecs
import sys
import re
from datetime import datetime


def clean_text(text):
    text = text.replace("<p>", "").replace("</p>", "\n")
    return re.sub('\.+', ".", text)


def main(articles_file, articles_output_dir, comments_file, comments_output_dir):

    '''For writing article text to txt files'''
    articles_df = pd.read_csv(articles_file)

    for idx, article in articles_df.iterrows():
        date = datetime.strptime(article['published_date'].split()[0], '%Y-%m-%d')

        folder_name = articles_output_dir + str(date.year)
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        file_name = folder_name + "/" + str(article['article_id']) + ".txt"
        text_file = codecs.open(file_name, "w", "utf-8")
        cleaned_text = clean_text(article['article_text'])
        text_file.write(cleaned_text)
        text_file.close()


    '''For writing comment text to txt files (one file per article)'''
    comments_df = pd.read_csv(comments_file)

    for idx, articles in comments_df.groupby('article_id'):
        folder_name = comments_output_dir

        file_name = folder_name + "/" + str(idx) + "_comments.txt"
        text_file = codecs.open(file_name, "w", "utf-8")
        cleaned_text = clean_text(articles['comment_text'].str.cat(sep="\n"))
        text_file.write(cleaned_text)


if __name__ == "__main__":
    articles_file = sys.argv[1]  # ./CSVs/gnm_articles.csv
    articles_output_dir = sys.argv[2]  # ./articles/

    comments_file = sys.argv[3]  # ./CSVs/gnm_comments.csv
    comments_output_dir = sys.argv[4]  # ./comments/

    main(articles_file, articles_output_dir, comments_file, comments_output_dir)