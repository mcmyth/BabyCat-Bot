const puppeteer = require('puppeteer');
var filename = process.argv[2];
var url = process.argv[3];
var w = process.argv[4];
var h = process.argv[5];
var proxy = process.argv[6];

(async () => {
    if (proxy === "false") {
        var browser = await puppeteer.launch({
            args: [
                '--proxy-server=',
                '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"',
            ],
            headless: true,
        });
    } else {

        var browser = await puppeteer.launch({
            args: [
                '--proxy-server=socks5://localhost:10808',
                '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"',
            ],
            headless: true,
        });
    }

    const page = await browser.newPage();
    try {
        await page.goto(url, {"waitUntil": "networkidle2"});
    } catch (err) {
        await browser.close();
    }

    function imagesHaveLoaded() {
        return Array.from(document.images).every((i) => i.complete);
    }

    await page.waitForFunction(imagesHaveLoaded);
    const header = await page.$('html');

    var doc = await page.evaluate((header) => {

        const {x, y, width, height} = header.getBoundingClientRect();
        return {x, y, width, height};
    }, header);
    console.log(doc);
    if (w === "auto" || w === null) w = doc.width;
    if (h === "auto" || h === null) h = doc.height;
    if (w > 1920) w = 1920;
    if (h > 5120) h = 5120;

    await page.setViewport({width: Math.round(w), height: Math.round(h)});
    await page.waitFor(2000);
    await page.screenshot({path: filename, quality: 76});


    await browser.close();
})();