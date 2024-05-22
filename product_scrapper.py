import os
import json
from bs4 import BeautifulSoup
from openai import OpenAI
from purify import remove_tags
from lxml import etree


class ProductPageScraper:
    def __init__(self, gpt_api_key):
        self.gpt_api_key = gpt_api_key
        self.client  = OpenAI(api_key=self.gpt_api_key)

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

    def get_page_schema_using_ai(self, url, required_variables):
        # Implement method to generate page schema using AI (GPT)
        html_data = self.fetch_html_page(url)
        if not html_data:
            return None
        host = url.split("/")[2]
        purified_html_data = remove_tags(
            f"purified/purified_{host}.html", html_content=html_data
        )
        schema = self.pridict(purified_html_data)
        with open(f"mappers/{host}.json", "w") as file:
            file.write(schema)
        return schema

    def pridict(self, html_content):
        prompt = f"""
		Extract the xpath and query selectors for getting the text based values of the following properties from the given product page HTML content so that they can be used to scrape the product details from the page. The properties to extract are as follows:

		- title
		- short_description
		- long_description
		- images
		- brand
		- vendor
		- collections
		- price
		- sku
		- has_multiple_variants
		- option1_name
		- option1_value
		- option2_name
		- option2_value
		- option3_name
		- option3_value

		the result should be in JSON fromat as below example:
		{{
			"title": {{"xpath": "", "cssSelector": "", "value_type": "string", "value": ""}},
			"short_description": {{"xpath": "", "cssSelector": "", "value_type": "string", "value": ""}},
			"long_description": {{"xpath": "", "cssSelector": "", "value_type": "html", "value": ""}},
			"images": {{"xpath": "", "cssSelector": "", "value_type": "string[]", "value": []}},
			"brand": {{"xpath": "", "cssSelector": "", "value_type": "string", "value": ""}},
			"vendor": {{"xpath": "", "cssSelector": "", "value_type": "string", "value": ""}},
			"collections": {{"xpath": "", "cssSelector": "", "value_type": "string[]", "value": []}},
			"price": {{"xpath": "", "cssSelector": "", "value_type": "string", "value": ""}},
			"sku": {{"xpath": "", "cssSelector": "", "value_type": "string", "value": ""}},
			"has_multiple_variants": {{"xpath": "", "cssSelector": "", "value_type": "boolean", "value": "false"}},
			"option1_name": {{"xpath": "", "cssSelector": "", "value_type": "string", "value": ""}},
			"option1_value": {{"xpath": "", "cssSelector": "", "value_type": "string", "value": ""}},
			"option2_name": {{"xpath": "", "cssSelector": "", "value_type": "string", "value": ""}},
			"option2_value": {{"xpath": "", "cssSelector": "", "value_type": "string", "value": ""}},
			"option3_name": {{"xpath": "", "cssSelector": "", "value_type": "string", "value": ""}},
			"option3_value": {{"xpath": "", "cssSelector": "", "value_type": "string", "value": ""}}
		}}

		If there is no value found for a property, return null against it.

		Product page HTML content:
		{html_content}
		"""

        # Send the request to OpenAI
        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        # Extract the response
        return response.choices[0].message.content

    def load_schema(self, url):
        host = url.split("/")[2]
        # Load schema from database (JSON file)
        with open(f"mappers/{host}.json", "r") as f:
            schema = json.load(f)
        return schema

    def scrape_product_page(self, url, required_variables):
        # Main method to scrape product page data
        schema = self.load_schema(url)
        html_data = self.fetch_html_page(url)
        if not html_data:
            return None
        if not schema:
            schema = self.get_page_schema_using_ai(url, required_variables)
        else:
            return self.extract_and_map(html_data, schema)
        
    def extract_and_map(self, html_content, mapper):
        """Extract the product details from the given HTML content using the provided mapper."""
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Initialize the product details dictionary
        product_details = {}

        # Extract the product details using the mapper
        for property_name, property_data in mapper.items():
            if type(property_data) is not dict:
                # TODO: Handle this case
                continue
            xpath = property_data.get("xpath")
            css_selector = property_data.get("cssSelector")
            value_type = property_data.get("value_type")
            extracted_value = None

            if xpath:
                parser = etree.HTMLParser()
                tree = etree.fromstring(html_content, parser)

                # Use XPath to extract data
                element = None
                extracted_values = tree.xpath(xpath)
                extracted_value = []
                if value_type == "html":
                    for e in extracted_values:
                        value = etree.tostring(e, encoding="unicode")
                        extracted_value.append(value)
                else:
                    if isinstance(extracted_values, list):
                        for e in extracted_values:
                            if isinstance(e, str):
                                extracted_value.append(e)
                            else:
                                value = e.text.strip() if e.text else None
                                if not value and isinstance(
                                    property_data.get("value"), str
                                ):
                                    value = tree.xpath(xpath + "/text()")
                                extracted_value.append(value)
            elif css_selector:
                # Find the element using the CSS selector
                element = soup.select_one(css_selector)
            else:
                element = None

            if element:
                # Extract the text content of the element
                extracted_value = element.get_text()
            elif type(extracted_value) is not list and extracted_value is not None:
                extracted_value = extracted_value.get_text()

            # Update the product details dictionary
            extracted_value = correct_type(value_type, extracted_value)
            product_details[property_name] = extracted_value

        return product_details


def correct_type(type, value):
    if not isinstance(value, list):
        return value
    else:
        if type == "string":
            if len(value) > 0 and value[1:] == value[:-1]:
                return value[0]
            else:
                return (
                    json.dumps(value).replace('"', "").replace("[", "").replace("]", "")
                )
        elif type == "string[]":
            return value if len(value) > 1 and isinstance(value[0], str) else None
        elif type == "html":
            return json.dumps(value).replace('"', "").replace("[", "").replace("]", "")
        elif type == "boolean":
            return value is not None and value != "" and value != []
        else:
            return value
