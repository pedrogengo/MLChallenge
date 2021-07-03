import logging
import requests
import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup


class Crawler:
    """A crawler allows us to enter a link and obtain information about it.
    
    With Crawler we can pass a URL and find other URLs that are referenced in it.

    Attributes:
        query_url: An URL to find linked urls.
        visited_urls: A list containing URLs that we already have in our
        database.
    """

    def __init__(self, url, visited_urls = []):
        self.visited_urls = visited_urls
        self.urls_to_visit = []
        self.query_url = url

    def download_url(self, url):
        return requests.get(url).text

    def get_linked_urls(self, url, html):
        paths = []
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            if path:
                if path.startswith('/'):
                    path = urljoin(url, path)
                paths.append(path)
        return paths

    def add_url_to_visit(self, url):
        self.count_references += 1
        if url not in self.visited_urls and url not in self.urls_to_visit:
            self.urls_to_visit.append(url)

    def crawl(self, url):
        html = self.download_url(url)
        for url in self.get_linked_urls(url, html):
            self.add_url_to_visit(url)

    def run(self):
        url = self.query_url
        logging.info(f'Crawling: {url}')
        try:
            self.crawl(url)
        except Exception:
            logging.exception(f'Failed to crawl: {url}')
        finally:
            self.visited_urls.append(url)


    def handler(event, context):
        visited_urls = []
        for record in event["Records"]:
            body = json.loads(record['body'])
            depth = body['Depth']
            query_url = body['Link']
            
            crawler = Crawler(query_url, visited_urls=visited_urls)
            crawler.run()
            if depth == 1:
                return 
            else:
                
        return crawler.urls_to_visit, crawler.count_references
