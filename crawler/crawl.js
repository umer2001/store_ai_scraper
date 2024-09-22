const puppeteer = require('puppeteer');
const { getContext, setContext } = require('./context');
const { waitFor, parseProxyString } = require('./utils');

async function launchBrowser() {
    const { proxy: proxyString } = getContext("body");
    const proxy = proxyString ? parseProxyString(proxyString) : null;
    // set User-Agent
    const userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36';
    const args = [
        '--no-sandbox',
        '--disable-setuid-sandbox',
    ];
    if (proxy?.url) {
        args.push(`--proxy-server=${proxy.url}`);
    }
    const browser = await puppeteer.launch({
        args: args,
    });
    const page = await browser.newPage();
    await page.setUserAgent(userAgent);
    // Set the proxy authentication credentials if required
    if (proxy?.username && proxy?.password) {
        await page.authenticate({ username: proxy.username, password: proxy.password });
    }
    setContext("browser", browser);
    setContext("page", page);
    return { page, browser };
}

async function runInBrowser(fn, ...args) {
    const { browser } = await launchBrowser();
    // const recorder = new PuppeteerScreenRecorder(page);
    // await recorder.start(`./video/${Math.random() * 1000}.mp4`);
    const result = await fn(...args);
    // await recorder.stop();
    await browser.close();
    return result;
}

async function getHTML({ url }) {
    const page = getContext("page");
    await page.goto(url, { waitUntil: 'networkidle0', timeout: process.env.PUPPETEER_TIMEOUT || 30000 });
    const html = await page.content();

    // const host = new URL(url).hostname;
    // const date = new Date().toISOString().slice(0, 10); // Format as YYYY-MM-DD
    // const filename = `${host}-${date}.html`;

    // // Ensure the output directory exists
    // const outputPath = path.join(__dirname, 'output');
    // fs.mkdirSync(outputPath, { recursive: true });

    // // Write the HTML to a file
    // fs.writeFileSync(path.join(outputPath, filename), html);
    return html;
}

async function getCatalogHTML(
    catalogUrl,
    pagenation = {
        pagenationType: null,
        xpath: null,
        cssSelector: null
    },
) {
    if (pagenation.pagenationType === 'Load More Button') {
        return [await loadMore(catalogUrl, pagenation)];
    }

    if (pagenation.pagenationType === 'Next Page Button') {
        return await nextPage(catalogUrl, pagenation);
    }

    return [await infiniteScroll(catalogUrl)];
}

async function nextPage(
    catalogUrl,
    pagenation = {
        pagenationType: null,
        xpath: null,
        cssSelector: null
    },
    pages = [],
    scapedPagesUrls = [],
    browser = null
) {
    if (scapedPagesUrls.includes(catalogUrl)) {
        await browser.close();
        return pages;
    }
    if (!browser) {
        browser = getContext("browser");
    }
    const page = getContext("page");
    await page.goto(catalogUrl, { waitUntil: 'networkidle0' });
    const html = await page.content();
    pages.push(html);
    scapedPagesUrls.push(catalogUrl);

    const res = await page.$$eval(pagenation.cssSelector, (pagenationElements) => {
        const pagenationElement = pagenationElements[pagenationElements.length - 1];
        if (!pagenationElement || pagenationElement.disabled) {
            return "pages";
        }
        pagenationElement.click()
    });
    if (res == "pages") {
        await browser.close();
        return pages;
    }
    console.log("waiting for url change....", page.url());
    await waitFor(2);
    const nextUrl = page.url();
    return await nextPage(nextUrl, pagenation, pages, scapedPagesUrls, browser);
}

async function loadMore(
    catalogUrl,
    pagenation = {
        pagenationType: null,
        cssSelector: null
    },
) {
    const page = getContext("page");
    await page.goto(catalogUrl, { waitUntil: 'networkidle0', timeout: process.env.PUPPETEER_TIMEOUT || 3000 });
    var html;
    do {
        console.log("in loop");
        await waitFor(5);
        const btn = await page.$(pagenation.cssSelector)
        if (!btn || html == await page.content()) {
            const endHeight = await page.evaluate("document.body.scrollHeight");
            await scrollSlowly(page, 0, 0.1, "up");
            await waitFor(0.5);
            await scrollSlowly(page, endHeight, 0.1);
            break;
        }
        html = await page.content();
        await page.evaluate((element) => {
            element.scrollIntoView();
            element.click();
        }, btn);
    } while (true);

    html = await page.content();
    return html;
}


async function infiniteScroll(
    catalogUrl
) {
    const { page } = getContext("page");
    await page.goto(catalogUrl, { waitUntil: 'networkidle0', timeout: process.env.PUPPETEER_TIMEOUT || 3000 });

    var times = 0;
    var previousHeight;
    do {
        console.log("times =>", times);
        if (previousHeight == await page.evaluate("document.body.scrollHeight") || times >= 10) {
            break;
        }
        previousHeight = await page.evaluate("document.body.scrollHeight");

        /*
            UP SCROLL
        */
        for (let hightPercent = previousHeight; hightPercent > previousHeight * 0.2; hightPercent -= 50) {
            await waitFor(0.1);
            await page.evaluate(`window.scrollTo(0, ${hightPercent})`);
        }

        /*
            DOWN SCROLL
        */
        // for (let hightPercent = previousHeight*0.2; hightPercent < previousHeight; hightPercent += 50) {
        //     await waitFor(0.5);
        //     await page.evaluate(`window.scrollTo(0, ${hightPercent})`);
        // }

        console.log("previousHeight", previousHeight);
        times += 1;
        await waitFor(10);
    } while (true)

    // await page.screenshot({
    //     fullPage: true,
    //     path: "video/ss.png"
    // })

    const html = await page.content();
    return html;
}

module.exports = {
    getHTML,
    getCatalogHTML,
    runInBrowser
};
