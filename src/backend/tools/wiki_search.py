import requests


class WikipediaSearch:
    API_URL = "https://en.wikipedia.org/w/api.php"

    HEADERS = {
        "User-Agent": "rag-chatbot-practice/1.0 (contact: your-email@example.com)"
    }

    def search(self, query: str, limit: int = 3):
        response = requests.get(
            self.API_URL,
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": limit,
                "format": "json",
            },
            headers=self.HEADERS,
            timeout=10,
        )
        response.raise_for_status()

        results = response.json()["query"]["search"]

        return [
            {
                "title": result["title"],
                "content": self.get_page(result["title"]),
            }
            for result in results
        ]

    def get_page(self, title: str):
        response = requests.get(
            self.API_URL,
            params={
                "action": "query",
                "prop": "extracts",
                "explaintext": 1,
                "titles": title,
                "format": "json",
                "formatversion": 2,
            },
            headers=self.HEADERS,
            timeout=10,
        )
        response.raise_for_status()

        pages = response.json()["query"]["pages"]

        if not pages:
            return ""

        return pages[0].get("extract", "")[:5000]

if __name__ == "__main__":
    wiki_search = WikipediaSearch()
    result = wiki_search.search("cimzia")
    print(result)