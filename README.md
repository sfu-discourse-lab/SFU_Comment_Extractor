# SFU_Comment_Extractor
Extract articles and comments from news sites

It collects and preprocesses Globe & Mail news data from both Factiva library and Online Globe & Mail, finally generates corpus for all the news article and comments data.

It has 2 major parts:
* Part 1 - Factiva data
* Part 2 - Online Globe & Mail

********************************************************************************

<b>PART 1 - Factiva Data</b>

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
* Mouse over the pop-up window, right click thr mouse and click `Save As`. Define the file name and choose `Format` as `Webpage, Complete`. Click `Save` and you will get an .htm file downloaded
* Normally, each .htm file contains 100 articles, unless it is the last .htm file in your search result

2. Create Google CSE Account
* With Google CSE (Custom Search Engine), you can do automated search 
* In the code used here, we just need <b>cx</b> (Custom Search Engine id), <b>key</b> (API Key)
* <b>In order to get cx</b>, visit [this website][1], create your own custom search engine and you will find `cx=...` through the url in the browser
* <b>In order to get key</b>, visit [Google Dev Center][2], then click `ENABLE API` and enable `Custom Search API`. Next, click `Credentials`, and click `Create Credential` to create the key

3. Generate CSV file from downloaded data
* The CSV file columns contain <b>all the index</b> used by Factiva articles, there are also 2 types of search queries generated from the article text, url of the article and the article id.
* We generated url for each article using Google CSE with the 2 types of queries. Article id is extracted from the url.
* Google CSE cannot find all the urls, because some urls have been removed after a certain time or the 2 types of search query may not work. Meanwhile Google CSE has daily search limits. So, each day we kept running the data collection code to update `Factiva_csv.csv` with found urls and updates `Factiva_uncaptured.csv` for articles without urls. Then in the next day, just re-run the rescue code to read `Factiva_uncaptured.csv` and update `Factiva_csv.csv`.
* Sample downloaded Factiva articles can be found under folder `Factiva_Downloads`
* Source code can be found under folder `Source_Code/Factiva_Source`
  * If you want to run the code, some paths may need to be changed. Check comments with `# YOU MAY NEED TO CHANGE THE PATH HERE`
  * Settings of Google CSE also need to be changed. Find comments `# YOU NEED TO SET CSE ID HERE`, `# YOU NEED TO SET CSE KEY HERE`
  * `generate_Factive_csv.py` - It runs all the downloaded articles and generated the initial `Factiva_csv.csv` & `factiva_uncaptured.csv`. The 2 types of search queries it uses are all from TD text
  * `rescue_Factiva_csv.py` - It checks Factiva_uncaptured.csv, run the same search queries as `generate_factive_csv.py` in order to find urls for the rest articles. If an article's url' can be found, its data will be added in `Factiva_csv.csv`, otherwise it stays in `Factive_uncaptured.csv`. The reason we kept those uncaptured articles all in `Factive_uncaptured.csv` is because sometimes Google CSE cannot find the url today but may find it tomorrow with the same search query. We are also using multiple `cx & key` too. Each day, we re-run this rescue code and update both `Factiva_csv.csv` and `Factiva_uncaptured.csv`
  * `rescue_Factive_csv_LP.py` - It is used after `rescue_Factiva_csv.py` can no longer find more urls for the left articles. Instead of using TD text as search query, the code here uses LP text. it updates `Factiva_csv.csv` and `Factiva_uncaptured.csv`, but the 2 search queries in these csv files are still the 2 search queries from TD text.
* Sample output can be found under folder `Sample_Resources/Factiva_CSV`, it contains `Factiva_csv.csv` & `factiva_uncaptured.csv`



[1]:https://cse.google.com/cse/all
[2]:https://console.developers.google.com/apis/dashboard