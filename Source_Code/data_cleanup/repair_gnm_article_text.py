from bs4 import BeautifulSoup
import requests
import os
import re
import time
import dbm
import csv
import pandas as pd

def _count_words(s):
	"""count the number of words in a paragraph
	Args:
		[String] s
	Return:
		[INT] number of words in the string
	"""
	return len(s.split(" "))

def get_page(url):
	"""get the page information
	Args:
		[String] URL: the URL to the page we try to parse

	Return:
		[Data Structure] page: the request response from the page
	"""
	print(url)
	page = ''
	while page == '':
		try:
			time.sleep(1)
			page = requests.get(url)
		except:
			print("Connection refused by the server..")
			print("Let me sleep for 5 seconds")
			print("ZZzzzz...")
			time.sleep(5)
			print("Was a nice sleep, now let me continue...")
			continue
	return page

def main(input_file):
	bound = 200
	df = pd.read_csv(input_file)
	# get the article with the text less than 200 words
	short_article_index = df.index[df.article_text.apply(_count_words) < bound]
	short_article_url = df.article_url[df.article_text.apply(_count_words) < bound]
	
	# reparsing the article of those URL with to the articles
	for i in short_article_index:
		page = get_page(df.article_url.iloc[i])
		soup = BeautifulSoup(page.content, 'html.parser')
		article_text = [p.get_text().encode('utf-8').strip() \
			for p in soup.find_all('p', class_="c-article-body__text")]
		if article_text:
			df.article_text.iloc[i] = "/n".join(article_text)
	print("NOTE: the new file named GNM_ARTICLES_NEW.CSV")
	df.to_csv("gnm_articles_new.csv",index=False)

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(description='the path to the gnm_articles.csv')
	parser.add_argument('input_file', type=str, help='the input file')
	args = parser.parse_args()
	main(args.input_file)
