from bs4 import BeautifulSoup


def remove_tags(output_file_path, html_content=None, html_file_path=None):
    if html_content is None and html_file_path is None:
        raise ValueError("Either 'html_content' or 'html_file_path' must be provided.")

    # Read the HTML file
    if html_file_path is not None:
        with open(html_file_path, "r", encoding="utf-8") as file:
            html_content = file.read()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, "lxml")

    # Tags to remove
    tags_to_remove = ["head", "header", "footer", "script", "svg"]

    # Find and remove specified tags
    for tag in tags_to_remove:
        for element in soup.find_all(tag):
            element.decompose()

    # Write the modified HTML back to a new file
    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write(str(soup))

    return str(soup)
