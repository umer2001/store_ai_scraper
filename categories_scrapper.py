import os
import json
from bs4 import BeautifulSoup
from openai import OpenAI


class CategoriesScraper:
    def __init__(self, gpt_api_key):
        self.gpt_api_key = gpt_api_key
        self.client = OpenAI(api_key=self.gpt_api_key)
        
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

    def map_categories(
        self,
        source_categories,
        target_categories=[
            "Biscuits, Crackers & Bread",
            "Bars",
            "Canned & Packaged Food",
            "Cereals",
            "Chocolate",
            "Cooking Ingredients & Oils",
            "Cooking Sauces & Meal Kits",
            "Crisps, Nuts & Snacking Fruit",
            "Fruit & Desserts",
            "Jams, Honey & Spreads",
            "Rice, Pasta & Noodles",
            "Snacking",
            "Sugar & Home Baking",
            "Snacks & Confectionery",
            "Sweets",
            "Table sauces, dressings & condiments",
            "Yeast",
            "Grain",
            "Seasonings / Condiments/ Ingredients",
            "Edible Oils And Fats",
            "Sugar",
            "Chocolate",
            "Yeast",
            "Sweeteners",
            "Straches & Derivatives",
            "Flour",
            "Beans",
            "Nuts & Kernels",
            "Body Care",
            "Dental",
            "Deodorants",
            "Face Coverings & Hand Sanitizers",
            "Facial Skincare",
            "Haircare & Styling",
            "Lifestyle & Wellbeing",
            "Men's Toiletries",
            "Perfumes, Aftershaves & Gift Sets",
            "Shampoo",
            "Shower, Bath & Hand Hygiene",
            "Sports Nutrition",
            "Suncare & Travel",
            "Toothpaste, Mouthwash & Toothbrush",
            "Vitamins, Minerals & Supplements",
            "Women's Toiletries",
            "Make Up & Beauty Accessories",
            "Hair Colourants & Dyes",
            "Nail Supplies",
            "Foot Care",
            "Speciality",
            "Health Foods",
            "Organic",
            "Vegetarian & Vegan",
            "Free From",
            "Fairtrade",
            "Halal",
            "Keto",
            "Kosher",
            "Coffee",
            "Fizzy & Soft Drinks",
            "Hot Chocolate & Malted Drinks",
            "Juices & Smoothies",
            "Kids Drinks",
            "Milkshakes & Milk Drinks",
            "Sports, Energy & Wellness Drinks",
            "Squash & Cordial",
            "Tea",
            "Water",
            "Beer & Cider",
            "Adult Soft Drinks & Mixers",
            "Liqueurs & Spirits",
            "Wine & Champagne",
            "Alcohol Free & Low Alcohol Drinks",
            "Wine",
            "Baby Milk",
            "Baby Food",
            "Baby Drinks",
            "Mums",
            "Nappies & Wipes",
            "Baby Toiletries",
            "Baby Healthcare",
            "Baby Accessories & Cleaning",
            "Baby Dental",
            "Toys & Kid's Zone",
            "HOUSEHOLD",
            "Accessories & Cleaning",
            "Bathroom",
            "Bedroom",
            "General Household",
            "Laundry",
            "Bar accessories",
            "Cookware & Bakeware",
            "Tableware & Kitchen Accessories",
            "Aromatherapy",
            "Diet & Detox",
            "Digestive Health",
            "Eye & Ear Health",
            "First Aid",
            "Flower Remedies",
            "Hair Treatments",
            "Hayfever & Allergies",
            "Homeopathic",
            "Intimate Care",
            "Immune, Cold & Flu",
            "Joints & Muscles",
            "Mosquito Repellants",
            "Pain Relief",
            "Skin Treatments",
            "Sexual Health",
            "Sleep & Relaxation",
            "Medical Tape, Bandages & Plasters",
            "Weight Management",
            "Smoking control",
            "Arts & Crafts",
            "Books",
            "Desk Storage & Filing",
            "Desk Supplies",
            "Notebooks, Pads & Organizers",
            "Office Supplies",
            "Pens, Pencils & Highlighters",
            "Printing & Laminating",
            "Packaging & Mailing",
            "Rulers & Geometry Sets",
            "Miscellaneous",
            "Artificial Grass & Lawn Turf",
            "BBQ's & BBQ Accessories",
            "Garden Hand Tools & Equipment",
            "Garden Power Tools",
            "Greenhouses & Growhouses",
            "Watering Hoses & Ponds",
            "DIY",
            "Asian Food",
            "African & Caribbean Food",
            "Mediterranean Food",
            "East Asian Food",
            "Polish Food",
            "Cat Food & Accessories",
            "Dog Food & Accessories",
            "Small Animal, Fish & Bird",
            "Pet Bigger Packs",
            "Pet Supplies",
            "Gift For Female",
            "Gift For Male",
            "Gift For Kids",
            "Specials Gifts",
            "Generals",
        ],
        batch_size=200,
        start_index=0,
        accumulated_result=None,
    ):
        if target_categories is None:
            return None
        if accumulated_result is None:
            accumulated_result = {}

        # Base case: if start_index is beyond the length of source_categories, return the accumulated result
        if start_index >= len(source_categories):
            return accumulated_result

        # Determine the end index for the current batch
        end_index = min(start_index + batch_size, len(source_categories))

        # Extract the current batch
        source_categories_keys = list(source_categories.keys())
        batch = source_categories_keys[start_index:end_index]

        # Create the prompt
        prompt = f"""
        Map source categories to the following standard categories, make sure all {len(batch)} source categories are mapped to one of the standard category:
        source categories:
        {batch}
        
        standard categories:
        {target_categories}
        
        The result should be in JSON format as below example:
        {{
            "standard_category1": ["source_category1", "source_category2", ...],
            "standard_category2": ["source_category3"],
        }}
        """

        # Send the request to OpenAI (mocked here, replace with actual request)
        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            response_format={"type": "json_object"},
            temperature=0.2,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )
        batch_result = json.loads(response.choices[0].message.content)

        # Combine the batch result with the accumulated result
        for target_category, source_categories_list in batch_result.items():
            # removeing halucinated categories
            if target_category not in target_categories:
                continue
            source_categories_final = []
            for cat in source_categories_list:
                if cat in source_categories_keys:
                    source_categories_final.append(cat)

            if target_category in accumulated_result:
                accumulated_result[target_category] += source_categories_final
            else:
                accumulated_result[target_category] = source_categories_final

        # Recursive call with the next batch
        return self.map_categories(
            source_categories,
            target_categories,
            batch_size,
            end_index,
            accumulated_result,
        )

    def extract_and_map_categories(self, url):
        source = self.extract_categories(url)
        mapped_categories = self.map_categories(source)
        # save the extracted data to a file
        with open(
            f"mapped_categories/{url.replace('https:', '').replace('/', '_')}.json", "w"
        ) as f:
            f.write(json.dumps(mapped_categories, indent=4))
        return mapped_categories


def safe_at(lst, index, default=None):
    try:
        return lst[index]
    except IndexError:
        return default
