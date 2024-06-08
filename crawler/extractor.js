const cheerio = require('cheerio');

const extractProductsLink = (htmlContent, selectors = {
    xpath: null,
    cssSelector: null
}) => {
    const $ = cheerio.load(htmlContent);
    const productLinks = [];
    if (selectors.cssSelector) {
        $(selectors.cssSelector).each((index, element) => {
            productLinks.push($(element).attr('href'));
        });
    }
    return productLinks;
}

module.exports = {
    extractProductsLink
};