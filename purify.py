from bs4 import BeautifulSoup, Comment
import htmlmin


def clean_html(
    output_file_path,
    html_content=None,
    html_file_path=None,
    tags_to_remove=[
        "head",
        "header",
        "footer",
        "script",
        "noscript",
        "svg",
        "iframe",
        "link",
        "meta",
        "style",
    ],
    attributes_to_keep=[
        "href",
        "src",
        "title",
        "class",
        "id",
        "name",
        "data",
        "type",
        "value",
    ]):
    if html_content is None and html_file_path is None:
        raise ValueError("Either 'html_content' or 'html_file_path' must be provided.")

    # Read the HTML file
    if html_file_path is not None:
        with open(html_file_path, "r", encoding="utf-8") as file:
            html_content = file.read()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, "lxml")

    # Find and remove specified tags
    for tag in tags_to_remove:
        for element in soup.find_all(tag):
            element.decompose()

    # Remove all comments
    for comment in soup.findAll(text=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Remove all attributes
    for tag in soup.find_all():
        for attribute in list(tag.attrs.keys()):
            if attribute not in attributes_to_keep:
                del tag[attribute]

    # Remove all href starting with javascript
    for tag in soup.find_all("a"):
        if tag.has_attr("href") and tag["href"].lower().startswith("javascript"):
            tag.decompose()

    # Minify the HTML content
    html_content = htmlmin.minify(str(soup), remove_empty_space=True)

    # Write the modified HTML back to a new file
    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write(html_content)

    return html_content
