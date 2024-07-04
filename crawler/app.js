const express = require('express');
const { getHTML, getCatalogHTML } = require('./crawl');
const { cleanHTML, getPagenationType, getProductSelector } = require('./utils');
const { extractProductsLink } = require('./extractor');
const app = express();

app.use(express.json());

// Endpoint to receive and return the URL
app.post('/scrape', async (req, res) => {
    const { url } = req.body;
    if (!url) {
        return res.status(400).json({ error: 'URL is required' });
    }
    html = await getHTML(url);
    return res.json({ html });
});

app.post('/scrape-catalog', async (req, res) => {
    const { url } = req.body;
    if (!url) {
        return res.status(400).json({ error: 'URL is required' });
    }

    html = await getHTML(url);
    const purifiedHTML = await cleanHTML(html);
    const pagenationType = await getPagenationType(purifiedHTML);
    console.log("pagenationType =>", pagenationType);
    const pageList = await getCatalogHTML(url, pagenationType);
    console.log("pageList length =>", pageList.length);

    // extraction

    const productSelector = await getProductSelector(purifiedHTML);
    console.log("productSelector =>", productSelector);

    var productLinks = [];
    pageList.forEach(pageHtml => {
        productLinks = productLinks.concat(extractProductsLink(pageHtml, productSelector));
    })

    return res.json({ productLinks });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
