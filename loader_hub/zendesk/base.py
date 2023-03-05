"""Zendesk reader."""
from typing import List
import json
import requests
from llama_index.readers.base import BaseReader
from llama_index.readers.schema.base import Document
from bs4 import BeautifulSoup


class ZendeskReader(BaseReader):
    """Zendesk reader. Reads data from a Zendesk workspace.

    Args:
        zendesk_subdomain (str): Zendesk subdomain
    """

    def __init__(self, zendesk_subdomain: str) -> None:
        """Initialize Zendesk reader."""
        self.zendesk_subdomain = zendesk_subdomain

    def load_data(self) -> List[Document]:
        """Load data from the workspace.

        Args:
            workspace_id (str): Workspace ID.
        Returns:
            List[Document]: List of documents.
        """
        results = []

        articles = self.get_all_articles()
        for article in articles:
            body = article['body']
            soup = BeautifulSoup(body, 'html.parser')
            body = soup.get_text()
            extra_info = {
                "id": article['id'],
                "title": article['title'],
                "url": article['html_url'],
                "updated_at": article['updated_at']
            }

            results.append(
                Document(
                    body,
                    extra_info=extra_info,
                )
            )

        return results

    def get_all_articles(self):
        articles = []
        next_page = None

        while True:
            response = self.get_articles_page(next_page)
            articles.extend(response['articles'])
            next_page = response['next_page']

            if next_page is None:
                break

        return articles

    def get_articles_page(self, next_page: str = None):
        if next_page is None:
            url = f"https://{self.zendesk_subdomain}.zendesk.com/api/v2/help_center/en-us/articles?per_page=100"
        else:
            url = next_page

        response = requests.get(url)

        response_json = json.loads(response.text)

        next_page = response_json.get('next_page', None)

        articles = response_json.get('articles', [])

        return {
            "articles": articles,
            "next_page": next_page
        }
