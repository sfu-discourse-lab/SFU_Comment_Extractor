Directory with scripts for data clean-up and preparation for various analyses

Description of files:

generate_articles_comments_files.py <br />
Generates .txt files for all the articles in gnm_articles.csv. Also generates txt files for all the comments contained in each article. (One comment file per article)

random_sample.py <br />
Generates a random subset of articles per year according to the number mentioned in the articles_per_year.csv file. Also generates the txt files for comments corresponding to the articles subset.

clean_text.py <br />
Imports normalize_csv_comments.py (https://github.com/sfu-discourse-lab/SFU_Comment_Extractor/blob/master/Source_Code/CSV_creation/normalize_csv_comments.py)
and cleans the text of the articles in a given folder (news_data_24Nov2017 in this case but can be used for any folder)

repair_gnm_article_text.py <br />
run the file by using: <br />
"python repair_gnm_article_text.py path_to_gnm_article_file" <br />
This file can be used to fix part of the short articles, which is shorter than 200 words, in the "gnm_article.csv" file. We input the gnm_article.csv file, and we parse the articles again to replace the previous articles. The newly parsed file named as "gnm_articles_new.csv".

