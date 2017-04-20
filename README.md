# SFU_Comment_Extractor
Extract articles and comments from news sites

It collects and preprocesses Globe & Mail news data from both Factiva library and Online Globe & Mail, finally generates corpus for all the news article and comments data.

It has 2 major parts:
* <b>Part 1 - Factiva data</b>
* <b>Part 2 - Online Globe & Mail</b>

********************************************************************************

PART 1 - Factiva Data

1. Manually download Gloab & Mail articles from Factiva library
* Login Factiva 
* In the `Date` section, select the date range. In our data, we chose `from 2012/01/01 to 2016/12/31`
* In the `Duplicates` section, select `Identical`, so that Factiva will remove identical duplicates
* In the `Source` section, type `The Globe and Mail (Canada)`
* In the `Subject` section, click `Or` and select `Editorials` and `Commentaries/Opinions` under `Content Types`
* In the `Language` section, select `English`
* Click `Search`
* After the results came out, at the top left corner, `Sort by` section, select `Sort by: Oldest First`
* At the top right corner, click `Display Option` and select `Full Article/Report plus Indexing`
* Select all the articles in a page, click `save as icon` in the top middle, and select `Article Format`
* A pop-up window will appear, and you will see index such as "SE", "HD", "BY", etc. on the left side of the text
* Mouse over the pop-up window, right click thr mouse and click `Save As`. Define the file name and choose `Format` as `Webpage, Complete`. Click `Save` and you will get an .htm file downloaded.
* Normally, each .htm file contains 100 articles, unless it is the last .htm file in your search result.

2. Generate CSV file from downloaded data
* The CSV file columns contain <b>all the index</b> used by Factiva articles, there are also 2 types of search queries generated from the article text, url of the article and the article id.
* We generated url for each article using Google Custom Search Engine (CSE) with the 2 types of queries. Article id is extracted from the url.
* Google CSE cannot find all the urls, because some urls have been removed after a certain time or the 2 types of search query may not work. Meanwhile Google CSE has daily search limits. So, each day we kept running the data collection code to update `Factiva_csv.csv` with found urls and updates `Factiva_uncaptured.csv` for articles without urls. Then in the next day, just re-run the rescue code to read `Factiva_uncaptured.csv` and update `Factiva_csv.csv`.
* Sample downloaded Factiva articles can be found under folder `Factiva_Downloads`
* Source code can be found under folder `Source_Code/Factiva_Source`
  * `generate_factive_csv.py` - It runs all the downloaded articles and generated the initial `Factiva_csv.csv` & `factiva_uncaptured.csv`
  * TO-DO: RESCUE CODE
* Sample output can be found under folder `Sample_Resources/Factiva_CSV`, it contains `Factiva_csv.csv` & `factiva_uncaptured.csv`
