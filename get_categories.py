from categories_scrapper import CategoriesScraper

urls = [
    "https://www.hollandandbarrett.com",
    "https://www.sainsburys.co.uk/webapp/wcs/stores/servlet/gb/groceries",
    "https://www.marksandspencer.com/",
]


scraper = CategoriesScraper()

for url in urls:
    print(url)
    scraper.extract_categories(url)
