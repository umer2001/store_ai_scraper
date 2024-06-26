class CatalogScraper:

    def scrape_catalog(self, url):
        """Get the links of all products from URL of catageory or catalog."""
        import requests

        # URL of the endpoint
        SERVICE_URL = "http://localhost:3000/scrape-catalog"

        # Data to be sent to the endpoint
        data = {"url": url}

        # Sending a POST request
        response = requests.post(SERVICE_URL, json=data)

        # Printing the response
        return response.json().get("productLinks")
