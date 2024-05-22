const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function getHTML(url) {
    // set User-Agent
    const userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36';
    const browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });
    const page = await browser.newPage();
    await page.setUserAgent(userAgent);
    await page.goto(url, { waitUntil: 'networkidle0' });
    const html = await page.content();

    // const host = new URL(url).hostname;
    // const date = new Date().toISOString().slice(0, 10); // Format as YYYY-MM-DD
    // const filename = `${host}-${date}.html`;

    // // Ensure the output directory exists
    // const outputPath = path.join(__dirname, 'output');
    // fs.mkdirSync(outputPath, { recursive: true });

    // // Write the HTML to a file
    // fs.writeFileSync(path.join(outputPath, filename), html);

    await browser.close();

    return html;
}

module.exports = getHTML;