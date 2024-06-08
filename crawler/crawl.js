const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const { PuppeteerScreenRecorder } = require('puppeteer-screen-recorder');

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

async function getCategorizedCatalogHTML(
    categoryUrl,
    pagenation = {
        pagenationType: null,
        xpath: null,
        cssSelector: null
    },
    pages = [],
    scapedPagesUrls = [],
    browser = null
) {
    if (scapedPagesUrls.includes(categoryUrl)) {
        await browser.close();
        return pages;
    }
    if (!browser) {
        browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });
    }
    console.log("starting with", categoryUrl);
    const userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36';
    const page = await browser.newPage();
    // const recorder = new PuppeteerScreenRecorder(page);
    // await recorder.start(`./video/${Math.random() * 1000}.mp4`);
    await page.setUserAgent(userAgent);
    await page.goto(categoryUrl, { waitUntil: 'networkidle0' });
    const html = await page.content();
    pages.push(html);
    scapedPagesUrls.push(categoryUrl);

    // scroll to the bottom of the page
    // await page.evaluate(() => {
    //     window.scrollTo(0, document.body.scrollHeight);
    // });

    if (pagenation.pagenationType === 'Infinite Scroll') {
        // Todo: Implement Infinite Scroll
        return []
    }
    else {
        const res = await page.$$eval(pagenation.cssSelector, (pagenationElements) => {
            const pagenationElement = pagenationElements[pagenationElements.length - 1];
            if (!pagenationElement || pagenationElement.disabled) {
                return pages;
            }
            pagenationElement.click()
        });
        if (res) {
            return pages;
        }
        await page.waitForNavigation({ waitUntil: 'networkidle0' });
        const nextUrl = page.url();
        return await getCategorizedCatalogHTML(nextUrl, pagenation, pages, scapedPagesUrls, browser);
    }
}

module.exports = {
    getHTML,
    getCategorizedCatalogHTML
};