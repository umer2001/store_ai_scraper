const express = require('express');
const { setContext, clearContext } = require('./context');
const { runInBrowser, getHTML, getCatalogHTML } = require('./crawl');
const { cleanHTML, getPagenationType, getProductSelector } = require('./utils');

const app = express();

app.use(express.json());

// Middleware to set req.body in context
app.use((req, res, next) => {
    setContext('body', req.body); // Store req.body in context
    next();
});

// Middleware to clear the context after request processing
app.use((req, res, next) => {
    res.on('finish', () => {
        clearContext(); // Clear the context when the response is finished
    });
    next();
});

// Endpoint to receive and return the URL
app.post('/scrape', async (req, res) => {
    const { url } = req.body;
    if (!url) {
        return res.status(400).json({ error: 'URL is required' });
    }
    html = await runInBrowser(getHTML, { url });
    return res.json({ html });
});

app.post('/scrape-catalog', async (req, res) => {
    const { url } = req.body;
    if (!url) {
        return res.status(400).json({ error: 'URL is required' });
    }

    html = await runInBrowser(getHTML, { url });
    const purifiedHTML = await cleanHTML(html);
    const pagenationType = await getPagenationType(purifiedHTML);
    console.log("pagenationType =>", pagenationType);
    const pageList = await runInBrowser(getCatalogHTML, { url, pagenationType });
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
