# SFU_Comment_Extractor
Extract articles and comments from news sites

It collects and preprocesses Globe & Mail news data from both Factiva library and Online Globe & Mail, finally generates corpus for all the news article and comments data.

It has 2 major parts:
* Part 1 - Factiva data
* Part 2 - Online Globe & Mail

********************************************************************************

<b>PART 1 - Factiva Data</b>

1. About Factiva
* [Factiva is a business information and research tool owned by Dow Jones & Company. Factiva aggregates content from both licensed and free sources, and provides organizations with search, alerting, dissemination, and other information management capabilities.][3]
* The reason we use Factiva databse is because, it collects all the Globe and Mail news articles data, but we are only interested in <b>Opinions</b> and <b>Editorials</b>, and Factiva allows us to do the article filtering.
* [Get access to Factiva][4]
* NOTE: Factiva data is not all 100% match original online articles.


2. Manually download Gloab & Mail articles from Factiva library
* Login Factiva. 
* In the `Date` section, select the date range. In our data, we chose `from 2012/01/01 to 2016/12/31`.
* In the `Duplicates` section, select `Identical`, so that Factiva will remove identical duplicates.
* In the `Source` section, type `The Globe and Mail (Canada)`.
* In the `Subject` section, click `Or` and select `Editorials` and `Commentaries/Opinions` under `Content Types`.
* In the `Language` section, select `English`.
* Click `Search`.
* After the results came out, at the top left corner, `Sort by` section, select `Sort by: Oldest First`.
* At the top right corner, click `Display Option` and select `Full Article/Report plus Indexing`.
* Select all the articles in a page, click `save as icon` in the top middle, and select `Article Format`.
* A pop-up window will appear, and you will see index such as "SE", "HD", "BY", etc. on the left side of the text.
* Mouse over the pop-up window, right click thr mouse and click `Save As`. Define the file name and choose `Format` as `Webpage, Complete`. Click `Save` and you will get an .htm file downloaded.
* Normally, each .htm file contains 100 articles, unless it is the last .htm file in your search result.

3. Create Google CSE Account
* With Google CSE (Custom Search Engine), you can do automated search.
* In the code used here, we just need <b>cx</b> (Custom Search Engine id), <b>key</b> (API Key).
* <b>In order to get cx</b>, visit [this website][1], create your own custom search engine and you will find `cx=...` through the url in the browser.
* <b>In order to get key</b>, visit [Google Dev Center][2], then click `ENABLE API` and enable `Custom Search API`. Next, click `Credentials`, and click `Create Credential` to create the key.

4. Generate CSV file from downloaded data
* The CSV file columns contain <b>all the index</b> used by Factiva articles, there are also 2 types of search queries generated from the article text, url of the article and the article id.
* We generated url for each article using Google CSE with the 2 types of queries. Article id is extracted from the url.
* Google CSE cannot find all the urls, because some urls have been removed after a certain time or the 2 types of search query may not work. Meanwhile Google CSE has daily search limits. So, each day we kept running the data collection code to update `Factiva_csv.csv` with found urls and updates `Factiva_uncaptured.csv` for articles without urls. Then in the next day, just re-run the rescue code to read `Factiva_uncaptured.csv` and update `Factiva_csv.csv`.
* Sample downloaded Factiva articles can be found under folder `Factiva_Downloads`.
* Source code can be found under folder `Source_Code/Factiva_Source`.
  * If you want to run the code, some paths may need to be changed. Check comments with `# YOU MAY NEED TO CHANGE THE PATH HERE`.
  * Settings of Google CSE also need to be changed. Find comments `# YOU NEED TO SET CSE ID HERE`, `# YOU NEED TO SET CSE KEY HERE`.
  * `generate_Factive_csv.py` - It runs all the downloaded articles and generated the initial `Factiva_csv.csv` & `factiva_uncaptured.csv`. The 2 types of search queries it uses are all from TD text.
  * `rescue_Factiva_csv.py` - It checks Factiva_uncaptured.csv, run the same search queries as `generate_factive_csv.py` in order to find urls for the rest articles. If an article's url' can be found, its data will be added in `Factiva_csv.csv`, otherwise it stays in `Factive_uncaptured.csv`. The reason we kept those uncaptured articles all in `Factive_uncaptured.csv` is because sometimes Google CSE cannot find the url today but may find it tomorrow with the same search query. We are also using multiple `cx & key` too. Each day, we re-run this rescue code and update both `Factiva_csv.csv` and `Factiva_uncaptured.csv`.
  * `rescue_Factive_csv_LP.py` - It is used after `rescue_Factiva_csv.py` can no longer find more urls for the left articles. Instead of using TD text as search query, the code here uses LP text. it updates `Factiva_csv.csv` and `Factiva_uncaptured.csv`, but the 2 search queries in these csv files are still the 2 search queries from TD text.
* Sample output can be found under folder `Sample_Resources/Factiva_CSV`, it contains `Factiva_csv.csv` & `factiva_uncaptured.csv`.
* After rescue_Factive_csv_LP.py can no longer find more urls for the left articles, we manually find urls through Bing website and update all the data into `Factiva_csv.csv`, and the final Factiva_uncaptured.csv became empty.


********************************************************************************

<b>PART 2 - Online Globe & Mail</b>

* Compared with Factiva data, we are using Globe & Mail online articles. Using the urls we collected in our `Factiva_csv.csv` as <b>seed urls</b>, we have crawled more urls within the time range `2012/01/01 - 2016/12/31` as <b>base urls</b>. There are 9100 distinct seed urls and 10399 distinct base urls. Based on the base urls, we further extracted article data files and comments data files.
* NOTE: On 2016/11/28, Globe & Mail started to change their website, by adding <b>reactions</b> into each comments, so that users can choose "Like", "Funny", "Wow", "Sad" or "Disagree". Meanwhile, all of their article comments created before 2016/11/28 totally disappeared from the website but some of these old comments were still extractable while other old comments were un-extractable. We tried to contact Globe & Mail but they could not guarantee all the old comments would either be kept in their database or be all recovered in the future. Therefore, in our code, we have methods to extract both old comments that are invisible from the website and new comments with reactions data.

1. Crawl base urls from seed urls
* Crawling is to extract new urls that appear in each seed url.
* Seed urls and base urls are all unique. Collected base urls should <b>all start with "http://www.theglobeandmail.com/opinion/"</b>. So if a seed url does not have this prefix, it will be filtered out in base urls.
* File `sample_seed_urls.txt` under folder `Sample_Resources/Online_Resources` are the sample seed urls. Seed urls all come from `Factiva_csv.csv`. `collect_seed_urls.py` under folder `Source_Code/Online_Source` extracts the seed urls from `Factiva_csv.csv` for you.
* `Python Scrapy` is the tool we use for online url crawling
  * [To install Scrapy][6]
* `article_base_url_spider.py` under folder `Source_Code/Online_Source` generates the base urls.
  * To run the code, in your terminal, `cd` to folder `Source_Code/Online_Source`, then type `sh run_article_base_url_spider.sh`. 
  * The input is a file of seed urls, check our `sample_seed_urls.txt` under folder `Sample_Resources/Online_Resources`. 
  * The output is a file of base urls, check our `sample_base_urls.txt` under folder `Sample_Resources/Online_Resources`.
  * You can check `Logs/log.txt` for code running logs.

2. Extract article data and comments before 2016/11/28
* As we mentioned above, Globe & Mail comments created before 2016/11/28 became invisible from the website but some were still extractable while other cannot be extracted when we were doing data collection and Globe & Mail didn't give us a clear answer.
* In this step, I have extratced all the article data for each base url, and those old comments before 2016/11/28
  * Each article url has 1 extracted article file.
  * Each article url has 1 comments file which include all the extractable old comments for this article.
  * If an article's comments are not extractable, we add the article id in another file as record.
* `old_article_comments_spider.py` does all the work in this step
  * To run the code, in your terminal, `cd` to folder `Source_Code/Online_Source`, then type `sh run_old_article_comments_spider.sh`. 
  * In the code, you also need to use your Globe & Mail user name and password. Check the line with commnet `# CHANGE THE USER AUTHENTICATION HERE`.
  * The API key of gigya used in this code is for public use. To find more info, [check this link][5]
  * The input is is a file of base urls, check our `sample_base_urls.txt` under folder `Sample_Resources/Online_Resources`.
  * The output are article data files, comments data files and empty comments file
    * Check our `ArticleRawData` folder under `Output` for sample article data files.
    * Check our `CommentsRawData` folder under `Output` for sample comments data files.
    * Check our `empty_comment_article_ids.txt` file under `Output` for sample empty comments collections. <b>All the ids here are article ids</b>
    * If there will be errors when extracting article or comments data, the error information along with article id/url will be saved in `error_article_ids.txt`, `error_comments_article_ids.txt` under folder `Output`
    * You can check `Logs/log.txt` for code running logs.
    
3. Extract comments with reactions
* Globe & Mail added reactions after 2016/11/28, allowing users to choose "Like", "Funny", "Wow", "Sad" or "Disagree" to express their feelings toward each comment. This piece of data is valuable to our future sentiment analysis. Therefore we also collected the comments data for each base url with reactions.
* The comments here majorly are new comments after 2016/11/28. 
* When we were collecting the data, Globe & Mail has recovered some old comments with empty reactions. However they could not confirm that all the old comments would be recovered, which means some old comments may still be invisible.
* Globe & Mail also starts to disable comments for some articles, because of the inappropriate amount of abusive comments, and therefore the extracted comments can be empty for some articles.
* In this step, we majorly use `Python selenium`, it is able to extract any web elements on a website if you are able to find the HTML tag for each web element.
* [To install Python selenium][7]
* `get_comment_reactions.py` under folder `Source_Code/Online_Source` extracts comments and reactions, as well as reaction counts
  * Extracted comments & reactions for each article will be saved as a JSON file in folder `Output/CommentReactionsRawData`.
  * If an article with empty comments, the article id will be added in `empty_comment_reactions.txt` under folder `Output`.
  * If there errors would happen during the data collection, the error info along with the comment url will be recorded in `error_comment_reactions.txt` under folder `Output`.



[1]:https://cse.google.com/cse/all
[2]:https://console.developers.google.com/apis/dashboard
[3]:https://en.wikipedia.org/wiki/Factiva
[4]:https://global.factiva.com/factivalogin/login.asp?productname=global
[5]:http://stackoverflow.com/questions/40049808/python-urllib-is-not-extracting-reader-comments-from-a-website
[6]:https://doc.scrapy.org/en/0.12/intro/install.html
[7]:https://pypi.python.org/pypi/selenium