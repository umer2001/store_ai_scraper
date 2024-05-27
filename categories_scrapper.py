import os
import json
from bs4 import BeautifulSoup


class CategoriesScraper:
    def fetch_html_page(self, url):
        """Get the HTML content of the given URL."""
        import requests

        # URL of the endpoint
        SERVICE_URL = "http://localhost:3000/scrape"

        # Data to be sent to the endpoint
        data = {"url": url}

        # Sending a POST request
        response = requests.post(SERVICE_URL, json=data)

        # Printing the response
        return response.json().get("html")

    def extract_links(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        links = soup.find_all("a")

        links_dict = {}
        for link in links:
            href = link.get("href")
            text = link.text.strip()
            links_dict[text] = href
        return links_dict

    def clean_links(self, categories, host):
        cleaned_categories = {}

        for category, link in categories.items():

            if link is None:
                continue

            if link.startswith("http") and (
                not link.startswith(f"https://{host}")
                and not link.startswith(f"http://{host}")
            ):
                continue
            # remove query parameters
            new_link = link.split("?")[0]

            # removing http://host or https://host
            new_link = new_link.replace(f"https://{host}", "").replace(
                f"http://{host}", ""
            )

            cat_slug = (
                safe_at(new_link.split("/"), -1)
                if safe_at(new_link.split("/"), -1) != ""
                else safe_at(new_link.split("/"), -2)
            )

            if cat_slug and self.is_parent_category(cat_slug, category, categories):
                continue

            cleaned_categories[category] = new_link
        return cleaned_categories

    def is_parent_category(self, cat_slug, category, categories):
        categories_copy = categories.copy()
        del categories_copy[category]
        for _, link in categories_copy.items():
            if link is not None and cat_slug in link:
                return True
        return False

    def find_category_path_keyword(self, categories):
        key_words_dict = {}
        for _, link in categories.items():
            splited = link.split("/")
            if len(splited) >= 2:
                keyword = link.split("/")[1]
            else:
                # Todo: handle it
                # keyword = link.split("/")[0]
                continue
            key_words_dict[keyword] = key_words_dict.get(keyword, 0) + 1
        return max(key_words_dict, key=key_words_dict.get)

    def remove_without_keywords(self, categories, keyword):
        cleaned_categories = {}
        for category, link in categories.items():
            if link.startswith(f"/{keyword}"):
                cleaned_categories[category] = link
        return cleaned_categories

    def extract_categories(self, url):
        """Extract the product details from the given HTML content using the provided mapper."""
        host = url.split("/")[2]

        html_content = self.fetch_html_page(url)

        categories_dict = self.extract_links(html_content)

        cleaned_categories = self.clean_links(categories_dict, host)
        keyword = self.find_category_path_keyword(cleaned_categories)
        keyword_cleaned_categories = self.remove_without_keywords(
            cleaned_categories, keyword
        )

        # save the extracted data to a file
        with open(
            f"categories/{url.replace('https:', '').replace('/', '_')}.json", "w"
        ) as f:
            f.write(json.dumps(keyword_cleaned_categories, indent=4))

        return keyword_cleaned_categories


def safe_at(lst, index, default=None):
    try:
        return lst[index]
    except IndexError:
        return default
