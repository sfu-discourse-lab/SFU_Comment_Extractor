#!/bin/sh

echo "Running Globe and Mail scraper"

scrapy runspider --logfile ../../Logs/log.txt article_base_url_spider.py

echo "Done!"