#!/bin/sh

echo "Running Globe and Mail scraper"

scrapy runspider -a startDate='2012-01-01' -a endDate='2016-12-31' --logfile ../../Logs/log.txt old_article_comments_spider.py

echo "Done!"