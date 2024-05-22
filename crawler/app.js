const express = require('express');
const getHTML = require('./crawl');
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

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
