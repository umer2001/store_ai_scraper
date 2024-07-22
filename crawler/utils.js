const fs = require('fs');
const os = require('os')
const { exec } = require('child_process');
const OpenAI = require('openai');

const openai = new OpenAI({
    apiKey: process.env['OPENAI_API_KEY']
});

const cleanHTML = async (htmlContent) => {
    const fileName = `${Math.floor(Math.random() * 1000)}.html`;
    const filePath = `${os.tmpdir()}/${fileName}`;
    // write the html content to a file
    fs.writeFileSync(filePath, htmlContent);

    // execute a command to purify the html content
    const command = `python3 /tmp/clean.py ${filePath}`;
    await new Promise((resolve, reject) => {
        return exec(command, (err, stdout, stderr) => {
            if (err || stderr) {
                console.error(err || stderr);
                return reject(err || stderr);
            }
            console.log(stdout);
            return resolve(stdout);
        });
    })

    return fs.readFileSync(`${os.tmpdir()}/purified_${fileName}`);
}

const getProductSelector = async (purifiedHtmlContent) => {
    const xpathPrompt = `
            Extract a generic xpath and css selector from the a tag, which will allow me to extract product page links (not the product image link) from the product cards given ecommerce website catalog page.
    
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
                "content": xpathPrompt,
            }
        ],
    });

    return JSON.parse(data.choices[0].message.content);
}

const getPagenationType = async (purifiedHtmlContent) => {
    const prompt = `
    What type of pagenation is being used in the given ecommerce website catalog page? also provide the selector for the reltive button or link.

    option 1: Load More Button
    option 2: Next Page Button
    option 3: Infinite Scroll
    option 4: None of the above

    html content:
    ${purifiedHtmlContent}

    I want the answer in json format like this:
    {
        "pagenationType": "Infinite Scroll"
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
            }
        ],
    });

    return JSON.parse(data.choices[0].message.content);
}

const waitFor = async (seconds) => {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve();
        }, seconds * 1000);
    });
}

module.exports = {
    cleanHTML,
    getProductSelector,
    getPagenationType,
    waitFor
};