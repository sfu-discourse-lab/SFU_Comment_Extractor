# Collect seed urls from Factiva_csv.csv
import csv


def main():
    factiva_csv_path = "../../Sample_Resources/Factiva_CSV/factiva_csv.csv"
    seed_urls_path = "../../Sample_Resources/Online_Resources/sample_seed_urls.txt"

    seed_urls = []
    distinct_article_ids = set()      # an article may have different urls but only has 1 article id
    with open(factiva_csv_path) as factiva_csv:
        csv_reader = csv.DictReader(factiva_csv)
        for r in csv_reader:
            url = r['URL']
            article_id = r['Article_ID']
            if article_id not in distinct_article_ids:
                distinct_article_ids.add(article_id)
                seed_urls.append(url)

    with open(seed_urls_path, 'a') as seed_urls_out:
        for seed_url in seed_urls:
            seed_urls_out.write(seed_url+"\n")
if __name__ == "__main__":
    main()