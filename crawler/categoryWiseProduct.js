const fs = require('fs');
const { exec } = require('child_process');
const { OpenAI } = require('openai');
const { getHTML, getCategorizedCatalogHTML } = require('./crawl');
const { extractProductsLink } = require('./extractor');

const openai = new OpenAI({
    apiKey: ""
});

async function main() {
    const urls = [
        "https://www.marksandspencer.com/l/home-and-furniture/home-furnishings/cushions",
        // "https://www.sainsburys.co.uk/gol-ui/groceries/food-cupboard/sugar-and-home-baking/baking-and-dessert-mixes/c:1019804",
        // "https://www.hollandandbarrett.com/shop/food-drink/honey-jams-spreads/honey/manuka-honey/"
    ];


    for (const url of urls) {
        const host = new URL(url).host;
        const htmlContent = await getHTML(url);

        const fileName = url.replace("https://", "").replace(/\//g, "_");
        // // write the html content to a file
        fs.writeFileSync(`../html/${fileName}.html`, htmlContent);

        // execute a command to purify the html content
        const command = `python ../clean.py ${fileName}.html`;
        exec(command, (err, stdout, stderr) => {
            if (err) {
                console.error(err);
                return;
            }
            console.log(stdout);
        });

        const purifiedHtmlContent = fs.readFileSync(`../purified/purified_${fileName}.html`);

        const prompt = `
            What type of pagenation is being used in the given ecommerce website catalog page? also provide the xpath and css selector for the relative button or link.
    
            option 1: Infinite Scroll
            option 2: Load More Button
            option 3: Next Page Button
            option 4: None of the above
    
            html content:
            ${purifiedHtmlContent}
    
            I want the answer in json format like this:
            {
                "pagenationType": "Infinite Scroll"
                "xpath": "",
                "cssSelector": ""
            }`;

        const xpathPrompt = `
            Extract the xpath and css selector from the a tag, which will allow me to extract product page link (not the product image link) from the product cards given ecommerce website catalog page.
    
            html content:
            ${purifiedHtmlContent}
    
            I want the answer in json format like this:
            {
                "xpath": "",
                "cssSelector": ""
            }`;

        const data = await openai.chat.completions.create({
            model: "gpt-4-turbo",
            response_format: { type: "json_object" },
            temperature: 0.2,
            messages: [
                {
                    "role": "user",
                    "content": prompt,
                    // "content": xpathPrompt,
                }
            ],
        });

        const result = JSON.parse(data.choices[0].message.content);

        console.log(result);
        // console.log(extractProductsLink(purifiedHtmlContent, result));

        const list = await getCategorizedCatalogHTML(url, result);
        console.log(list);
    }


}

main();