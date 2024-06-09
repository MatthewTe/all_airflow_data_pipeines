import requests
from datetime import datetime, timedelta
import os
from bs4 import BeautifulSoup
import requests
import time 
import sqlalchemy as sa
from urllib.parse import parse_qs
from typing import TypedDict
import os
from datetime import datetime
import uuid
import pandas as pd 
import random

from .html_parsing import extract_article_content, extract_articles_display_page

class LoopPageConfig(TypedDict):
    db_url: str
    query_param_str: str
    article_category: str
    db_category: str

def process_loop_page(config: LoopPageConfig):

    db_url = config['db_url']   
    query_param_str = config['query_param_str']
    article_category =  config['article_category']
    db_category = config['db_category']

    LocalDevEngine: sa.engine.Engine = sa.create_engine(db_url)
    with LocalDevEngine.connect() as conn, conn.begin():
        conn.execute(sa.text("""
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                title TEXT,
                url TEXT,
                type TEXT,
                content TEXT,
                source TEXT,
                extracted_date TEXT,
                published_date TEXT
            );
        """)
        )

    headers_lst = [
        {"User-Agent":'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'},
        {"User-Agent":'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0'},
        {"User-Agent":'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1'},
        {"User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393'}
    ]
    base_url = f'https://tt.loopnews.com/category/{article_category}'
    article_base_url = 'https://tt.loopnews.com'
    query_params = parse_qs(query_param_str.lstrip("?"))

    article_extracted_date = datetime.now().strftime("%B %d, %Y %I:%M %p")

    print("Making request to article thumbnail page")
    articles_response: requests.Response = requests.get(base_url, params=query_params, headers=random.choice(headers_lst))
    print(f"Article thumbnail http response: {articles_response.status_code}")

    if not articles_response.ok:
        print(f"Unable to grab article for {articles_response.url}")
        print(articles_response.content)
        return

    page_content = extract_articles_display_page(articles_response.content)
    print(f"Extracted {len(page_content['articles'])} page content from {articles_response.url}")


    # Then we extract all of the article content from each of the pages:
    articles_to_insert = []
    if len(page_content['articles']) < 1:
        print(f"No Articles found for page {articles_response.url}")
    else:

        # Checking the articles against existing articles in the db:
        article_url: tuple[str] = tuple([article['url'] for article in page_content['articles']])
        
        with LocalDevEngine.connect() as conn, conn.begin():

            unique_title_query = sa.text(f'SELECT url FROM articles WHERE url IN {article_url}')

            existing_articles = [
                row[0] for row in conn.execute(
                    unique_title_query
                    #{'article_titles':article_titles}
                )
            ]

            unique_articles = [article for article in page_content['articles'] if article["url"] not in existing_articles]

        if len(unique_articles) == 0:
            print("No unique articles found. Reached end of dataset. Stopping....")
            return

        for article in unique_articles:

            print("Looping through articles for ingestion")
            print("Making individual article http request")
            single_page_response = requests.get(f"{article_base_url}{article['url']}", headers=random.choice(headers_lst))
            print(f"Full article http response: {single_page_response.status_code}")
            if not single_page_response.ok:
                continue
            
            single_artice_content = extract_article_content(single_page_response.content)

            # Comparing the date from the article thumbnail on the articl display page conten to the date value from the article:
            if article["published_date"] == single_artice_content["published_date"]:
                print("Published date from display page is the same as date from single article content date")
                article_published_date = single_artice_content["published_date"]
            else:
                print(f"Comparing publish dates is different: article_thumbnail: {article['published_date']} vs {single_artice_content['published_date']}")
                print("Setting to null.")
                article_published_date = None
            
            unique_url_hash = uuid.uuid5(uuid.NAMESPACE_URL, article['url'])
            new_article = {
                "id": str(unique_url_hash),
                "title": single_artice_content['title'],
                "url": article["url"],
                "type": config["db_category"],
                "content": single_artice_content["content"],
                "source": "https://tt.loopnews.com",
                "extracted_date": article_extracted_date,
                "published_date": article_published_date 
            }
        
            articles_to_insert.append(new_article)
            print(f"Added article to article list {new_article}. List has {len(articles_to_insert)}")
            time.sleep(random.choice(range(1, 5)))

        if len(articles_to_insert) < 1:
            print("No articles sucessfully extracted. List is empty. Performing no ingestion")
        else:
            print(f"Attempting to execute an ingestion query for the following articles: {articles_to_insert}")
            print(articles_to_insert)
            with LocalDevEngine.connect() as conn, conn.begin():
                try:
                    insert_query = sa.text("""
                        INSERT INTO articles 
                            (id, title, url, type, content, source, extracted_date, published_date)
                        VALUES 
                            (:id, :title, :url, :type, :content, :source, :extracted_date, :published_date)
                        """
                    )

                    result = conn.execute(insert_query, articles_to_insert)
                    print(f"Inserted {result.rowcount} rows into the Table")

                except Exception as e:
                    print("Error in inserting records into the database.")
                    wal_df = pd.DataFrame.from_records(articles_to_insert)
                    wal_df.to_csv("wal_errored.csv")
                    print(e.with_traceback(None))
                    raise e 

                time.sleep(random.choice(range(1, 5)))

            if not page_content['next_page']:
                print("Next page not found for the article thumbnail page")
                return 
            

            new_config: LoopPageConfig = {
                'article_category': article_category,
                'db_category': db_category,
                'db_url': db_url,
                'query_param_str': page_content['next_page']
            }

            process_loop_page(new_config)


if __name__ == "__main__":

    # Basic tests:
    '''

    db_url = ''

    crime_config: LoopPageConfig = {
        "query_param_str": '?page=0',
        "article_category": "looptt-crime",
        'db_category': "crime",
        'db_url':db_url
    }
    process_loop_page(crime_config)   

    politics_config: LoopPageConfig = {
    "query_param_str": '?page=170',
        "article_category": "looptt-politics",
        'db_category': "politics",
        'db_url':db_url
    }
    process_loop_page(politics_config)   

    carribean_config: LoopPageConfig = {
        "query_param_str": '?page=250',
        "article_category": "looptt-caribbean-news",
        'db_category': "caribbean-news",
        'db_url':db_url
    }
    process_loop_page(carribean_config)   
    '''