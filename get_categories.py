from categories_scrapper import CategoriesScraper

urls = [
    "https://www.hollandandbarrett.com",
    "https://www.sainsburys.co.uk/webapp/wcs/stores/servlet/gb/groceries",
    "https://www.marksandspencer.com/",
]


scraper = CategoriesScraper(gpt_api_key="")


for url in urls:
    print(url)
    scraper.extract_and_map_categories(url)
